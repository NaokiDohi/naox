from typing import Callable, Optional

from pyweb.http.request import HTTPRequest
from pyweb.http.response import HTTPResponse
from routers.urls import url_patterns


class URLResolver:
    def resolve(self, request: HTTPRequest) -> Optional[Callable[[HTTPRequest], HTTPResponse]]:
        """
        URL解決を行う
        pathにマッチするURLパターンが存在した場合は、対応するviewを返す
        存在しなかった場合は、Noneを返す
        """
        # pathに対応するview関数があれば、関数を取得して呼び出し、レスポンスを生成する
        # for-else文はforが最後まで実行された時にelseが実行される。
        # breakが呼ばれた場合実行されない。
        for url_pattern in url_patterns:
            match = url_pattern.match(request.path)
            if match:
                # URLパラメータが含まれている場合は.groupdict()メソッド
                # でパラメータが辞書{"user_id":""}で取得できる。
                print(f'match.groupdict(): {match.groupdict()}')
                request.params.update(match.groupdict())
                return url_pattern.view
        return None
             