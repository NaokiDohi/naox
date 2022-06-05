from dataclasses import dataclass, field

# dataclassデコレーターを使用するとinitメソッドを書かなくても良くなる
# データ型を定義する時には、@dataclassを使用すると良い
@dataclass
class HTTPRequest:
    path: str
    method: str
    http_version: str
    body: bytes
    headers: dict = field(default_factory=dict)

# class HTTPRequest:
#     path: str
#     method: str
#     http_version: str
#     headers: dict
#     body: bytes

#     def __init__(
#         self, path: str = "", method: str = "", http_version: str = "", headers: dict = None, body: bytes = b""
#     ):
#         # Noneをデフォルト値にしたのは、
#         # 関数呼び出しの際にデフォルト値を共有しないようにするため
#         if headers is None:
#             headers = {}

#         self.path = path
#         self.method = method
#         self.http_version = http_version
#         self.headers = headers
#         self.body = body