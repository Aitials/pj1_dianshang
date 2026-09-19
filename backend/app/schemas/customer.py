from decimal import Decimal
from pydantic import BaseModel


class CustomerRankItem(BaseModel):
    customer_unique_id: str
    sales: Decimal
    count_order: int


class CustomerRankResponse(BaseModel):
    top: int
    customer_rank: list[CustomerRankItem]

class CustomerRepurchaseResponse(BaseModel):
    total_customers: int
    repeat_customers: int
    repurchase_rate: float

class CustomerGeoItem(BaseModel):
    city: str
    state: str
    customer_count: int
    lat: float
    lng: float


class CustomerGeoResponse(BaseModel):
    items: list[CustomerGeoItem]