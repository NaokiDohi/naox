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

    # レスポンスボディを生成
    body = render("now.html", context)

    return HTTPResponse(body=body)

def show_request(request: HTTPRequest) -> HTTPResponse:
    """
    HTTPリクエストの内容を表示するHTMLを生成する
    """
    # decode("utf-8", "ignore")はバイトデータをutf-8でデコード、
    # デコードできない文字は無視してそのまま表示
    context = {"request": request, "headers": pformat(request.headers), "body": request.body.decode("utf-8", "ignore")}
    # レスポンスボディを生成
    body = render("show_request.html", context)

    return HTTPResponse(body=body)

def parameters(request: HTTPRequest) -> HTTPResponse:
    """
    POSTパラメータを表示するHTMLを表示する
    """
    # GETリクエストの場合は、405を返す
    if request.method == "GET":
        body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"

        return HTTPResponse(body=body, status_code=405)

    elif request.method == "POST":
        # urllib.parse.parse_qs()は、URLエンコードされた文字列を辞書へパースする関数
        # {str:list}の辞書を返す
        context = {"params": pformat(urllib.parse.parse_qs(request.body.decode()))}
        body = render("parameters.html", context)
        
        return HTTPResponse(body=body)

def user_profile(request: HTTPRequest) -> HTTPResponse:
    context = {"user_id": request.params["user_id"]}

    body = render("user_profile.html", context)

    return HTTPResponse(body=body)

def set_cookie(request: HTTPRequest) -> HTTPResponse:
    return HTTPResponse(headers={"Set-Cookie": "username=Naoki"})

def login(request: HTTPRequest) -> HTTPResponse:
    if request.method == "GET":
        body = render("login.html", {})
        return HTTPResponse(body=body)

    elif request.method == "POST":
        post_params = urllib.parse.parse_qs(request.body.decode())
        username = post_params["username"][0]
        email = post_params["email"][0]

        headers={"Location": "/welcome"}
        cookies={"username": username, "email": email}

        return HTTPResponse(status_code=302, headers=headers, cookies=cookies)


def welcome(request: HTTPRequest) -> HTTPResponse:
    # Cookieにusernameが含まれていなければ、ログインしていないとみなして/loginへリダイレクト
    if "username" not in request.cookies:
        return HTTPResponse(status_code=302, headers={"Location": "/login"})

    # Welcome画面を表示
    username = request.cookies["username"]
    email = request.cookies["email"]
    body = render("welcome.html", context={"username": username, "email": email})

    return HTTPResponse(body=body)