from pydantic import BaseModel


class InventoryItem(BaseModel):
    product_id: str
    quantity: int
    safe_stock: int


class InventoryListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[InventoryItem]

class InventoryitemResponse(BaseModel):
    product_id: str
    before: int
    after: int

class InventoryWarningItem(BaseModel):
    product_id: str
    quantity: int
    safe_stock: int

class InventoryWarningResponse(BaseModel):
    need_fill: list[InventoryWarningItem]