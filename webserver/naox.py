import socket
from datetime import datetime

class Naox:
    """
    TCP通信を行うサーバーを表すクラス
    """
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
            
            # レスポンスボディを生成
            response_body = "<html><body><h1>It works!</h1></body></html>"

            # レスポンスラインを生成
            response_line = "HTTP/1.1 200 OK\r\n"
            # レスポンスヘッダーを生成
            response_header = ""
            response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
            response_header += "Host: Naox/0.1\r\n"
            response_header += f"Content-Length: {len(response_body.encode())}\r\n"
            response_header += "Connection: Close\r\n"
            response_header += "Content-Type: text/html\r\n"

            # ヘッダーとボディを空行でくっつけた上でbytesに変換し、レスポンス全体を生成する
            response = (response_line + response_header + "\r\n" + response_body).encode()

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
