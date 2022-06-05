import os
import re
import traceback
from datetime import datetime
from socket import socket
from threading import Thread
from typing import Tuple

import settings
from pyweb.http.request import HTTPRequest
from pyweb.http.response import HTTPResponse
from routers.urls import URL_VIEW

class Worker(Thread):
    """
    TCP通信を行うサーバーを表すクラス
    """
    print(f'BASE_DIR: {settings.BASE_DIR}')
    print(f'STATIC_ROOT: {settings.STATIC_ROOT}')

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

            # pathに対応するview関数があれば、関数を取得して呼び出し、レスポンスを生成する
            if request.path in URL_VIEW:
                view = URL_VIEW[request.path]
                response = view(request)

            # pathがそれ以外のときは、静的ファイルからレスポンスを生成する
            else:
                try:
                    # レスポンスボディを生成
                    response_body = self.get_static_file_content(request.path)
                    # Content-Typeを指定
                    content_type = None
                    response = HTTPResponse(status_code=200, body=response_body, content_type=content_type)

                except OSError:
                    # レスポンスを取得できなかった場合は、ログを出力して404を返す
                    traceback.print_exc()
                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    content_type = "text/html; charset=UTF-8"
                    response = HTTPResponse(status_code=404, body=response_body, content_type=content_type)
            
            # レスポンスラインを生成
            response_line = self.build_response_line(response)
            # レスポンスヘッダーを生成
            response_header = self.build_response_header(request, response)
            # ヘッダーとボディを空行で結合した後bytesに変換し、レスポンス全体を生成
            response = (response_line + response_header + "\r\n").encode() + response.body

            # クライアントへレスポンスを送信する
            self.client_socket.send(response)
        
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

        return HTTPRequest(method=method, path=path, http_version=http_version, body=request_body, headers=headers)

    def get_static_file_content(self, path: str) -> bytes:
        """
        リクエストpathから、staticファイルの内容を取得する
        """
        # settingsモジュールにSTATIC_ROOTが存在すればそれを取得し、
        # なければデフォルトの値を使用する。
        default_static_root = os.path.join(os.path.dirname(__file__), "../../static")
        static_root = getattr(settings, "STATIC_ROOT", default_static_root)

        # pathの先頭の/を削除し、相対パスにする
        # 消去するのはos.path.join(base, path)の仕様上　
        # 第2引数pathに/で始まる絶対パスを与えると第一引数baseが無視される
        relative_path = path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(static_root, relative_path)

        # ファイルからレスポンスボディを生成
        with open(static_file_path, "rb") as f:
            return f.read()

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
            else:
                ext = ""
            # 拡張子からMIME Typeを取得
            # 対応していない拡張子の場合、octet-streamとする
            response.content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

        # レスポンスヘッダーを生成
        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: Naox/0.6\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"

        return response_header