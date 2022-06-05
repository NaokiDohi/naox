import socket

from workerthread import WorkerThread

class WebServer:
    """
    TCP通信を行うサーバーを表すクラス
    """

    def serve(self):
        """
        サーバーを起動する
        """

        print("=== Server: サーバーを起動します ===")

        try:
            # socketを生成
            server_socket = self.create_server_socket()

            # 1つのリクエストの処理が完了し、コネクションを終了後、
            # ループの先頭にもどり再度リクエストを待機する。
            # 実行者が明示的に終了させない限りリクエストを待機し続ける
            while True:
                # 外部からの接続を待ち、接続があったらコネクションを確立する
                print("=== Server: クライアントからの接続を待ちます ===")
                # 返り値はクライアントとの接続が確立された新しいsocketインスタンスとクライアントアドレス
                # server_socketは次のコネクションを受け付ける
                (client_socket, address) = server_socket.accept()
                print(f"=== Server: クライアントとの接続が完了しました(コネクションが確立する) remote_address: {address} ===")

                # クライアントを処理するスレッドを作成
                thread = WorkerThread(client_socket, address)
                # 新規スレッドを作成 start()でスレッドが作成されると同時にrun()が実行される
                thread.start()

        finally:
            print("=== Server: サーバーを停止します。 ===")

    def create_server_socket(self) -> socket:
        """
        通信を待ち受けるためのserver_socketを生成する
        :return:
        """
        # socketを生成
        server_socket = socket.socket()
        # socketはデフォルト設定だと、プログラムが終了してもしばらくportを掴んだまま離さず、
        # 連続してプログラムが起動できなくなってしまうため、設定を変更しています。
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # socketをlocalhostのポート8080番に割り当てる
        # ======================================
        # プログラム内で予約
        server_socket.bind(("localhost", 8080))
        # 割り当ての実行(占有)　他のプログラムは使えなくなる
        # 引数は同時に受け付けるクライアントの数
        server_socket.listen(10)
        return server_socket


if __name__ == '__main__':
    server = WebServer()
    # サーバーを起動させるメソッド
    server.serve()
