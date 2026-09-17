from decimal import Decimal
from pydantic import BaseModel


class DashboardOverviewResponse(BaseModel):
    total_orders :int
    delivered_orders :int
    canceled_orders :int
    total_sales :Decimal
    class Config:
        from_attributes = True