import os
import socket
from datetime import datetime

class Naox:
    """
    TCP通信を行うサーバーを表すクラス
    """

    # 実行ファイルのあるディレクトリ
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 静的配信するファイルを置くディレクトリ
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    print(f'BASE_DIR: {BASE_DIR}')
    print(f'STATIC_ROOT: {STATIC_ROOT}')

    def serve(self):
        """
        サーバーを起動する
        """

        print("=== サーバーを起動します ===")

        try:
            # socketを生成
            server_socket = socket.socket()
            # socketはデフォルト設定だと、プログラムが終了してもしばらくportを掴んだまま離さず、
            # 連続してプログラムが起動できなくなってしまうため、設定を変更しています。
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # socketをlocalhostのポート8080番に割り当てる
            # ======================================
            # プログラム内で予約
            server_socket.bind(("localhost", 5050))
            # 割り当ての実行(占有)　他のプログラムは使えなくなる
            # 引数は同時に受け付けるクライアントの数
            server_socket.listen(10)

            # 外部からの接続を待ち、接続があったらコネクションを確立する
            print("=== クライアントからの接続を待ちます ===")
            # 返り値はクライアントとの接続が確立された新しいsocketインスタンスとクライアントアドレス
            # server_socketは次のコネクションを受け付ける
            (client_socket, address) = server_socket.accept()
            print(f"=== クライアントとの接続が完了しました(コネクションが確立する)remote_address: {address} ===")

            # クライアントから送られてきたデータをbytes型で取得する
            # 引数はネットワークバッファ(到着したデータをためておく所)から一回で取得するバイト数。
            # recv()は呼び出した時点で溜まっているデータを、4096バイトずつ繰り返し取得し、全て取得する。
            request = client_socket.recv(4096)

            # クライアントから送られてきたデータをファイルに書き出す
            with open("server_recv.txt", "wb") as f:
                f.write(request)

            # リクエスト全体を
            # 1. リクエストライン(1行目)
            # 2. リクエストヘッダー(2行目〜空行)
            # 3. リクエストボディ(空行〜)
            # にパースする
            request_line, remain = request.split(b"\r\n", maxsplit=1)
            request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

            # リクエストラインをパースする
            method, path, http_version = request_line.decode().split(" ")

            # pathの先頭の/を削除し、相対パスにする
            # 消去するのはos.path.join(base, path)の仕様上　
            # 第2引数pathに/で始まる絶対パスを与えると第一引数baseが無視される
            relative_path = path.lstrip("/")
            # ファイルのpathを取得
            static_file_path = os.path.join(self.STATIC_ROOT, relative_path)

            # ファイルからレスポンスボディを生成
            with open(static_file_path, "rb") as f:
                response_body = f.read()

            # レスポンスラインを生成
            response_line = "HTTP/1.1 200 OK\r\n"
            # レスポンスヘッダーを生成
            response_header = ""
            response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            response_header += "Host: Naox/0.2\r\n"
            response_header += f"Content-Length: {len(response_body)}\r\n"
            response_header += "Connection: Close\r\n"
            response_header += "Content-Type: text/html\r\n"

            # ヘッダーとボディを空行で結合した後bytesに変換し、レスポンス全体を生成
            response = (response_line + response_header + "\r\n").encode() + response_body

            # クライアントへレスポンスを送信する
            client_socket.send(response)

            # 返事は特に返さず、通信を終了させる
            client_socket.close()

        finally:
            print("=== サーバーを停止します。 ===")


if __name__ == '__main__':
    server = Naox()
    # サーバーを起動させるメソッド
    server.serve()
