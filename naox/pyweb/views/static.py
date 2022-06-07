import os
import traceback

import settings
from pyweb.http.request import HTTPRequest
from pyweb.http.response import HTTPResponse

def static(request: HTTPRequest) -> HTTPResponse:
    """
    静的ファイルからレスポンスを取得する
    """

    try:
        # settingsモジュールからSTATIC_ROOTを取得
        static_root = getattr(settings, "STATIC_ROOT")

        # pathの先頭の/を削除し、相対パスにしておく
        # 消去するのはos.path.join(base, path)の仕様上　
        # 第2引数pathに/で始まる絶対パスを与えると第一引数baseが無視される
        relative_path = request.path.lstrip("/")

        # ファイルのpathを取得
        static_file_path = os.path.join(static_root, relative_path)

        with open(static_file_path, "rb") as f:
            response_body = f.read()
        
        # Content-Typeを指定
        content_type = None

        return HTTPResponse(status_code=200, body=response_body, content_type=content_type)

    except OSError:
        # ファイルを取得できなかった場合は、ログを出力して404を返す
        traceback.print_exc()

        response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
        content_type = "text/html; charset=UTF-8"
        
        return HTTPResponse(status_code=404, body=response_body, content_type=content_type)