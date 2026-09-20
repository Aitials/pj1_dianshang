from datetime import datetime

from pydantic import BaseModel


class OperationLogItem(BaseModel):
    id: int
    operator: str
    action: str
    target: str | None = None
    detail: str | None = None
    created_at: datetime | None = None


class OperationLogListResponse(BaseModel):
    total: int
    items: list[OperationLogItem]
