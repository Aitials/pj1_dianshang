from datetime import datetime

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

class Replenishitresponse(BaseModel):
    product_id: str
    avg_daily_sales:float
    suggest_quantity : float
    current_quantity: int
    safety_stock: int

class ReplenishResponse(BaseModel):
    items: list[Replenishitresponse]

class inventory_logs(BaseModel):
    id : int
    product_id : str
    change :int
    before :int
    after :int
    reason :str
    operator :str
    created_at :datetime

class inventory_logsResponse(BaseModel):
    total : int
    page : int
    page_size: int
    items : list[inventory_logs]