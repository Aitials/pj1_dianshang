from typing import Any, List, Optional ,TypeVar ,Generic
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel ,Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None

def ok(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}

def ok_page(items: List[Any], total: int, page: int, page_size: int) -> dict:
    return {"code": 0, "message": "success",
            "data": {"items": items, "total": total, "page": page, "page_size": page_size}}

def fail(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}
