from typing import Optional, Union, List
from dataclasses import dataclass, field

from pyweb.http.cookie import Cookie

@dataclass
class HTTPResponse:
    body: Union[bytes, str] = b""
    content_type: Optional[str] = None # str型またはNoneを表す型 Nullable型
    status_code: int = 200
    headers: dict = field(default_factory=dict) # {<header-name>: <header-value>}
    cookies: List[Cookie] = field(default_factory=list)

# class HTTPResponse:
#     status_code: int
#     body: Union[bytes, str]
#     content_type: Optional[str] # str型またはNoneを表す型 Nullable型
#     headers: dict
#     cookies: List[Cookie]

#     def __init__(
#         self,
#         status_code: int = 200,
#         body: Union[bytes, str] = b"",
#         content_type: str = None,
#         headers: dict = None,
#         cookies: List[Cookie] = None,
#     ):
#         if headers is None:
#             headers = {}
#         if cookies is None:
#             cookies = []

#         self.status_code = status_code
#         self.body = body
#         self.content_type = content_type
#         self.headers = headers
#         self.cookies = cookies