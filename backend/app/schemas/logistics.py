from pydantic import BaseModel


class LogisticsOverviewResponse(BaseModel):
    avg_delivery_days: float
    total_delivered: int
    on_time_count: int
    delayed_count: int
    on_time_rate: float
    delay_rate: float