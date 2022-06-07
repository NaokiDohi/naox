from typing import Callable

from pyweb.http.request import HTTPRequest
from pyweb.http.response import HTTPResponse
from pyweb.views.static import static
from routers.urls import url_patterns


class URLResolver:
    def resolve(self, request: HTTPRequest) -> Callable[[HTTPRequest], HTTPResponse]:
        """
        URL解決を行う
        pathにマッチするURLパターンが存在した場合は、対応するviewを返す
        存在しなかった場合は、static viewを返す
        """
        # pathに対応するview関数があれば、関数を取得して呼び出し、レスポンスを生成する
        for url_pattern in url_patterns:
            match = url_pattern.match(request.path)
            if match:
                # URLパラメータが含まれている場合は.groupdict()メソッド
                # でパラメータが辞書{"user_id":""}で取得できる。
                print(f'match.groupdict(): {match.groupdict()}')
                request.params.update(match.groupdict())
                return url_pattern.view

        return static
             