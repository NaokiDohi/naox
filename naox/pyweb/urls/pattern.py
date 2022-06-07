import re
from re import Match
from typing import Callable, Optional

from pyweb.http.request import HTTPRequest
from pyweb.http.response import HTTPResponse
    
class URLPattern:
    pattern: str
    view: Callable[[HTTPRequest], HTTPResponse]
    # Callableは関数(呼び出し可能オブジェクト:()を付けて呼び出せるオブジェクト)を表す型注釈
    # この場合はHTTPRequestインスタンスを受け取り、HTTPResponseを返す関数を意味する。

    def __init__(self, pattern: str, view: Callable[[HTTPRequest], HTTPResponse]):
        self.pattern = pattern
        self.view = view

    def match(self, path: str) -> Optional[Match]:
        """
        pathがURLパターンにマッチするか判定する
        マッチした場合はMatchオブジェクトを返し、マッチしなかった場合はNoneを返す
        """
        # URLパターンを正規表現パターンに変換する
        # ex) '/user/<user_id>/profile' => '/user/(?P<user_id>[^/]+)/profile'
        # url_patternの中の
        # <(.+?)>任意の1文字の1回以上の繰り返しを
        # (?P<user_id>[^/]+?) 直前の文字０個か1個マッチし、/以外の繰り返しを表す正規表現に置換
        pattern = re.sub(r"<(.+?)>", r"(?P<\1>[^/]+)", self.pattern)
        return re.match(pattern, path)