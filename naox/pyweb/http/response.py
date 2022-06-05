from typing import Optional
from dataclasses import dataclass, field

@dataclass
class HTTPResponse:
    status_code: int
    body: bytes
    content_type: Optional[str] # str型またはNoneを表す型 Nullable型

# class HTTPResponse:
#     status_code: int
#     body: bytes
#     content_type: Optional[str] # str型またはNoneを表す型 Nullable型

#     def __init__(self, status_code: int, body: bytes = b"", content_type: str = None):
#         self.status_code = status_code
#         self.body = body
#         self.content_type = content_type