import textwrap
import urllib.parse
from datetime import datetime
from pprint import pformat
from typing import Tuple, Optional

def now() -> Tuple[str, bytes, Optional[str]]:
    """
    現在時刻を表示するHTMLを生成する
    """
    html = f"""\
        <html>
        <body>
            <h1>Now: {datetime.now()}</h1>
        </body>
        </html>
    """
    
    # レスポンスラインを生成
    response_line = "HTTP/1.1 200 OK\r\n"
    # レスポンスボディを生成
    response_body = textwrap.dedent(html).encode()
    # Content-Typeを指定
    # これは、動的コンテンツを利用する場合
    # pathからはレスポンスボディのフォーマットを特定することができないから
    content_type = "text/html; charset=UTF-8"

    return response_line, response_body, content_type

def show_request(
        method: str,
        path: str,
        http_version: str,
        request_header: dict,
        request_body: bytes,
    ) -> Tuple[str, bytes, Optional[str]]:
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
                {method} {path} {http_version}
            </p>
            <h1>Headers:</h1>
            <pre>{pformat(request_header)}</pre>
            <h1>Body:</h1>
            <pre>{request_body.decode("utf-8", "ignore")}</pre>
            
        </body>
        </html>
    """

    # レスポンスラインを生成
    response_line = "HTTP/1.1 200 OK\r\n"
    # レスポンスボディを生成
    response_body = textwrap.dedent(html).encode()
    # Content-Typeを指定
    content_type = "text/html; charset=UTF-8"

    return response_line, response_body, content_type

def parameters(
        method: str,
        request_body: bytes,
    ) -> Tuple[str, bytes, Optional[str]]:
    """
    POSTパラメータを表示するHTMLを表示する
    """
    if method == "GET":
        response_line = "HTTP/1.1 405 Method Not Allowed\r\n"
        response_body = b"<html><body><h1>405 Method Not Allowed</h1></body></html>"
        content_type = "text/html; charset=UTF-8"

    elif method == "POST":
        # urllib.parse.parse_qs()は、URLエンコードされた文字列を辞書へパースする関数
        # {str:list}の辞書を返す
        post_params = urllib.parse.parse_qs(request_body.decode())
        html = f"""\
            <html>
            <body>
                <h1>Parameters:</h1>
                <pre>{pformat(post_params)}</pre>                        
            </body>
            </html>
        """
        # レスポンスラインを生成
        response_line = "HTTP/1.1 200 OK\r\n"
        # レスポンスボディを生成
        response_body = textwrap.dedent(html).encode()
        # Content-Typeを指定
        content_type = "text/html; charset=UTF-8"
    
    return response_line, response_body, content_type