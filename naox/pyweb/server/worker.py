import re
import traceback
import textwrap
from datetime import datetime
from socket import socket
from threading import Thread
from typing import Tuple

from pyweb.http.request import HTTPRequest
from pyweb.http.response import HTTPResponse
from pyweb.urls.resolver import URLResolver

class Worker(Thread):
    """
    TCP通信を行うサーバーを表すクラス
    """

    # 拡張子とMIME Typeの対応
    # ブラウザで日本語を表示させる為、日本語に対応したエンコーディングを指定
    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
        "csv": "text/csv",
    }

    # ステータスコードとステータスラインの対応
    STATUS_LINES = {
        200: "200 OK",
        302: "302 Found",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
    }

    def __init__(self, client_socket: socket, address: Tuple[str, int]):
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:
        """
        クライアントと接続済みのsocketを引数として受け取り、
        リクエストを処理してレスポンスを送信する
        """
        try:
            # クライアントから送られてきたデータをbytes型で取得する
            # 引数はネットワークバッファ(到着したデータをためておく所)から一回で取得するバイト数。
            # recv()は呼び出した時点で溜まっているデータを、4096バイトずつ繰り返し取得し、全て取得する。
            request_bytes = self.client_socket.recv(4096)

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request_bytes)

            # HTTPリクエストをパースする
            request = self.parse_http_request(request_bytes)

            # URL解決を行う
            view = URLResolver().resolve(request)

            # レスポンスを生成する
            response = view(request)

            # レスポンスボディを変換
            # bodyがstr型の場合、bytes型へ変換
            if isinstance(response.body, str):
                response.body = textwrap.dedent(response.body).encode()

            # レスポンスラインを生成
            response_line = self.build_response_line(response)

            # レスポンスヘッダーを生成
            response_header = self.build_response_header(request, response)

            # ヘッダーとボディを空行で結合した後bytesに変換し、レスポンス全体を生成
            response_bytes = (response_line + response_header + "\r\n").encode() + response.body

            # クライアントへレスポンスを送信する
            self.client_socket.send(response_bytes)
        
        except Exception:
            # リクエストの処理中に例外が発生した場合は、
            # コンソールにエラーログを出力し処理を続行する
            print("=== Worker: リクエストの処理中にエラーが発生しました ===")
            traceback.print_exc()

        finally:
            # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
            print(f"=== Worker: クライアントとの通信を終了します remote_address: {self.client_address} ===")
            self.client_socket.close()

    def parse_http_request(self, request: bytes) -> HTTPRequest:
        """
        HTTPリクエストを
        1. method: str
        2. path: str
        3. http_version: str
        4. request_header: dict
        5. request_body: bytes
        に分割/変換する
        """

        # リクエスト全体を
        # 1. リクエストライン(1行目)
        # 2. リクエストヘッダー(2行目〜空行)
        # 3. リクエストボディ(空行〜)にパースする
        # ボディは画像やPDFなど、文字列ではなくバイナリデータが
        # 送られてくる可能性があるためバイナリのまま扱う
        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

        # リクエストラインをパースする
        method, path, http_version = request_line.decode().split(" ")

        # リクエストヘッダーを辞書にパースする
        headers = {}
        # CRLFでsplit
        for header_row in request_header.decode().split("\r\n"):
            # 正規表現の1つの":"と、0個以上の空白でsplit
            key, value = re.split(r": *", header_row, maxsplit=1)
            headers[key] = value

        cookies = {}
        if "Cookie" in headers:
            # str から list へ変換 
            # "name1=value1; name2=value2" => ["name1=value1", "name2=value2"]
            # Cookieは1つと限らない。複数の場合は;区切りで渡される。
            cookie_strings = headers["Cookie"].split("; ")
            # list から dict へ変換
            # ["name1=value1", "name2=value2"] => {"name1": "value1", "name2": "value2"}
            for cookie_string in cookie_strings:
                name, value = cookie_string.split("=", maxsplit=1)
                cookies[name] = value

        return HTTPRequest(method=method, path=path, http_version=http_version, headers=headers, cookies=cookies, body=request_body)

    def build_response_line(self, response: HTTPResponse) -> str:
        """
        レスポンスラインを構築する
        """
        status_line = self.STATUS_LINES[response.status_code]
        return f"HTTP/1.1 {status_line}"

    def build_response_header(self, request: HTTPRequest, response: HTTPResponse) -> str:
        """
        レスポンスヘッダーを構築する
        """

        # ヘッダー生成の為、Content-Typeを取得
        # Content-Typeが指定されていない場合はpathから特定する
        if response.content_type is None:
            # pathから拡張子を取得
            if "." in request.path:
                ext = request.path.rsplit(".", maxsplit=1)[-1]
                # 拡張子からMIME Typeを取得
                # 対応していない拡張子の場合、octet-streamとする
                response.content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
            else:
                # pathに拡張子がない場合はhtml扱いとする
                response.content_type = "text/html; charset=UTF-8"

        # レスポンスヘッダーを生成
        # 基本ヘッダーの生成
        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: Naox/0.6\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"

        # Cookieヘッダーの生成
        for cookie in response.cookies:
            cookie_header = f"Set-Cookie: {cookie.name}={cookie.value}"
            if cookie.expires is not None:
                cookie_header += f"; Expires={cookie.expires.strftime('%a, %d %b %Y %H:%M:%S GMT')}"
            if cookie.max_age is not None:
                cookie_header += f"; Max-Age={cookie.max_age}"
            if cookie.domain:
                cookie_header += f"; Domain={cookie.domain}"
            if cookie.path:
                cookie_header += f"; Path={cookie.path}"
            if cookie.secure:
                cookie_header += "; Secure"
            if cookie.http_only:
                cookie_header += "; HttpOnly"

            response_header += cookie_header + "\r\n"

        # その他ヘッダーの生成
        for header_name, header_value in response.headers.items():
            response_header += f"{header_name}: {header_value}\r\n"

        return response_header