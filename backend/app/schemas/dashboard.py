from decimal import Decimal
from pydantic import BaseModel


class DashboardOverviewResponse(BaseModel):
    total_orders :int
    delivered_orders :int
    canceled_orders :int
    total_sales :Decimal
    class Config:
        from_attributes = True

class Productitemresponse(BaseModel):
    product_id: str
    sales: Decimal
    sold_count : int


class Productrankresponse(BaseModel):
    product_ranking: list[Productitemresponse]

class CategoryRankingItem(BaseModel):
    category_name: str
    sales : Decimal

class CategoryRankingResponse(BaseModel):
    category_ranking: list[CategoryRankingItem]

class Selleritem(BaseModel):
    seller_id: str
    sales: Decimal

class Seller_rankresponse(BaseModel):
    seller_ranking: list[Selleritem]

class Send_time_rateresponse(BaseModel):
    send_time_rate: float
