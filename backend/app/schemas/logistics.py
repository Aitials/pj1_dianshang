from pydantic import BaseModel


class LogisticsOverviewResponse(BaseModel):
    avg_delivery_days: float
    total_delivered: int
    on_time_count: int
    delayed_count: int
    on_time_rate: float
    delay_rate: float

class logistics_geoit(BaseModel):
    state : str
    order_count : int
    avg_fulfillment_days : float
    delay_rate : float

class logistics_geoResponse(BaseModel):
    geo : list[logistics_geoit]

class logistics_ratingResponse(BaseModel):
    on_time_avg_score:float
    delayed_avg_score: float
    on_time_count: float
    delayed_count: float