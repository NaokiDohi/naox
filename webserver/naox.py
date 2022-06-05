import os
import socket
import traceback
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

    # 拡張子とMIME Typeの対応
    MIME_TYPES = {
        "html": "text/html",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
        "csv": "text/csv",
    }

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

            while True:
                # 外部からの接続を待ち、接続があったらコネクションを確立する
                print("=== クライアントからの接続を待ちます ===")
                # 返り値はクライアントとの接続が確立された新しいsocketインスタンスとクライアントアドレス
                # server_socketは次のコネクションを受け付ける
                (client_socket, address) = server_socket.accept()
                print(f"=== クライアントとの接続が完了しました(コネクションが確立する)remote_address: {address} ===")

                # 1つのリクエストの処理が完了し、コネクションを終了後、
                # ループの先頭にもどり再度リクエストを待機する。
                # 実行者が明示的に終了させない限りリクエストを待機し続ける
                try:
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
                    try:
                        with open(static_file_path, "rb") as f:
                            response_body = f.read()

                        # レスポンスラインを生成
                        response_line = "HTTP/1.1 200 OK\r\n"

                    except OSError:
                        # ファイルが見つからなかった場合は404を返す
                        response_line = "HTTP/1.1 404 Not Found\r\n"
                        response_body = b"<html><body><h1>404 Not Found</h1></body></html>"

                    # ヘッダー生成の為、Content-Typeを取得
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
                    response_header += "Host: Naox/0.3\r\n"
                    response_header += f"Content-Length: {len(response_body)}\r\n"
                    response_header += "Connection: Close\r\n"
                    response_header += f"Content-Type: {content_type}\r\n"

                    # ヘッダーとボディを空行で結合した後bytesに変換し、レスポンス全体を生成
                    response = (response_line + response_header + "\r\n").encode() + response_body

                    # クライアントへレスポンスを送信する
                    client_socket.send(response)

                except Exception:
                    # リクエストの処理中に例外が発生した場合は、
                    # コンソールにエラーログを出力し処理を続行する
                    print("=== リクエストの処理中にエラーが発生しました ===")
                    traceback.print_exc()

                finally:
                    # 例外が発生した場合も、発生しなかった場合も、TCP通信のcloseは行う
                    client_socket.close()

        finally:
            print("=== サーバーを停止します。 ===")


if __name__ == '__main__':
    server = Naox()
    # サーバーを起動させるメソッド
    server.serve()
