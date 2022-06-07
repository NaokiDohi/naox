from typing import Optional, Union
from dataclasses import dataclass, field

@dataclass
class HTTPResponse:
    body: Union[bytes, str]
    content_type: Optional[str] = None # str型またはNoneを表す型 Nullable型
    status_code: int = 200

# class HTTPResponse:
#     status_code: int
#     body: Union[bytes, str]
#     content_type: Optional[str] # str型またはNoneを表す型 Nullable型

#     def __init__(self, status_code: int = 200, body: Union[bytes, str] = b"", content_type: str = None):
#         self.status_code = status_code
#         self.body = body
#         self.content_type = content_type