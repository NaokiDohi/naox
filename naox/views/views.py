import textwrap
import urllib.parse
from datetime import datetime
from pprint import pformat

from pyweb.http.request import HTTPRequest
from pyweb.http.response import HTTPResponse
from pyweb.templates.renderer import render

# Viewの関数引数のインターフェースを統一し、
# 呼び出しの際に必要な引数が何かを考える必要がないようにする
def now(request: HTTPRequest) -> HTTPResponse:
    """
    現在時刻を表示するHTMLを生成する
    """
    context = {"now": datetime.now()}
    html = render("now.html", context)
    
    # レスポンスボディを生成
    body = textwrap.dedent(html).encode()
    # Content-Typeを指定
    # これは、動的コンテンツを利用する場合
    # pathからはレスポンスボディのフォーマットを特定することができないから
    content_type = "text/html; charset=UTF-8"

    return HTTPResponse(status_code=200, body=body, content_type=content_type)

def show_request(request: HTTPRequest) -> HTTPResponse:
    """
    HTTPリクエストの内容を表示するHTMLを生成する
    """
    # decode("utf-8", "ignore")はバイトデータをutf-8でデコード、
    # デコードできない文字は無視してそのまま表示
    html = f"""\
        <html>
        <body>
            <h1>Request Line:</h1>
            <p>
                {request.method} {request.path} {request.http_version}
            </p>
            <h1>Headers:</h1>
            <pre>{pformat(request.headers)}</pre>
            <h1>Body:</h1>
            <pre>{request.body.decode("utf-8", "ignore")}</pre>
            
        </body>
        </html>
    """

    # レスポンスボディを生成
    body = textwrap.dedent(html).encode()
    # Content-Typeを指定
    content_type = "text/html; charset=UTF-8"

    return HTTPResponse(status_code=200, body=body, content_type=content_type)

def parameters(request: HTTPRequest) -> HTTPResponse:
    """
    POSTパラメータを表示するHTMLを表示する
    """
    # GETリクエストの場合は、405を返す
    if request.method == "GET":
        status_code = 405
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        content_type = "text/html; charset=UTF-8"

    elif request.method == "POST":
        # urllib.parse.parse_qs()は、URLエンコードされた文字列を辞書へパースする関数
        # {str:list}の辞書を返す
        post_params = urllib.parse.parse_qs(request.body.decode())
        html = f"""\
            <html>
            <body>
                <h1>Parameters:</h1>
                <pre>{pformat(post_params)}</pre>                        
            </body>
            </html>
        """

        status_code = 200
        # レスポンスボディを生成
        body = textwrap.dedent(html).encode()
        # Content-Typeを指定
        content_type = "text/html; charset=UTF-8"
    
    return HTTPResponse(status_code=status_code, body=body, content_type=content_type)

def user_profile(request: HTTPRequest) -> HTTPResponse:
    user_id = request.params["user_id"]

    html = f"""\
        <html>
        <body>
            <h1>プロフィール</h1>
            <p>ID: {user_id}
        </body>
        </html>
    """

    status_code = 200
    body = textwrap.dedent(html).encode()
    content_type = "text/html; charset=UTF-8"

    return HTTPResponse(status_code=status_code, body=body, content_type=content_type)