from webserver import WebServer

if __name__ == '__main__':
    server = WebServer()
    # サーバーを起動させるメソッド
    server.serve()