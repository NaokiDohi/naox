import os
import re
import textwrap
import traceback
import urllib.parse
from datetime import datetime
from pprint import pformat
from socket import socket
from threading import Thread
from typing import Tuple, Optional

from views import views

class WorkerThread(Thread):
    """
    TCP通信を行うサーバーを表すクラス
    """
    # 実行ファイルのあるディレクトリ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静的配信するファイルを置くディレクトリ
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    print(f'BASE_DIR: {BASE_DIR}')
    print(f'STATIC_ROOT: {STATIC_ROOT}')

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

    # pathとview関数の対応
    URL_VIEW = {
        "/now": views.now,
        "/show_request": views.show_request,
        "/parameters": views.parameters,
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
            request = self.client_socket.recv(4096)

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # HTTPリクエストをパースする
            method, path, http_version, request_header, request_body = self.parse_http_request(request)

            response_body: bytes
            content_type: Optional[str] # str型またはNoneを表す型 Nullable型
            response_line: str

            # pathに対応するview関数があれば、関数を取得して呼び出し、レスポンスを生成する
            if path in self.URL_VIEW:
                view = self.URL_VIEW[path]
                response_line, response_body, content_type = view(
                    method, path, http_version, request_header, request_body
                )

            # pathがそれ以外のときは、静的ファイルからレスポンスを生成する
            else:
                try:
                    # レスポンスラインを生成
                    response_line = "HTTP/1.1 200 OK\r\n"
                    # レスポンスボディを生成
                    response_body = self.get_static_file_content(path)
                    # Content-Typeを指定
                    content_type = None


                except OSError:
                    # レスポンスを取得できなかった場合は、ログを出力して404を返す
                    traceback.print_exc()
                    response_line = "HTTP/1.1 404 Not Found\r\n"
                    response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                    content_type = "text/html; charset=UTF-8"

            # レスポンスヘッダーを生成
            response_header = self.build_response_header(path, response_body, content_type)
            # ヘッダーとボディを空行で結合した後bytesに変換し、レスポンス全体を生成
            response = (response_line + response_header + "\r\n").encode() + response_body

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

    def parse_http_request(self, request: bytes) -> Tuple[str, str, str, dict, bytes]:
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

        return method, path, http_version, headers, request_body

    def get_static_file_content(self, path: str) -> bytes:
        """
        リクエストpathから、staticファイルの内容を取得する
        """
        # pathの先頭の/を削除し、相対パスにする
        # 消去するのはos.path.join(base, path)の仕様上　
        # 第2引数pathに/で始まる絶対パスを与えると第一引数baseが無視される
        relative_path = path.lstrip("/")
        # ファイルのpathを取得
        static_file_path = os.path.join(self.STATIC_ROOT, relative_path)

        # ファイルからレスポンスボディを生成
        with open(static_file_path, "rb") as f:
            return f.read()

    def build_response_header(self, path: str, response_body: bytes, content_type: Optional[str]) -> str:
        """
        レスポンスヘッダーを構築する
        """

        # ヘッダー生成の為、Content-Typeを取得
        # Content-Typeが指定されていない場合はpathから特定する
        if content_type is None:
            # pathから拡張子を取得
            if "." in path:
                ext = path.rsplit(".", maxsplit=1)[-1]
            else:
                ext = ""
            # 拡張子からMIME Typeを取得
            # 対応していない拡張子の場合、octet-streamとする
            content_type = self.MIME_TYPES.get(ext, "application/octet-stream")

        # レスポンスヘッダーを生成
        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
        response_header += "Host: Naox/0.6\r\n"
        response_header += f"Content-Length: {len(response_body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {content_type}\r\n"

        return response_header