from pydantic import BaseModel

class AdjustInventory(BaseModel):
    change: int
    reason: str = None
    operator: str = None
