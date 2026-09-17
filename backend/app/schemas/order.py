from datetime import datetime
from pydantic import BaseModel
from decimal import Decimal

class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    order_status: str

    order_purchase_timestamp: datetime | None = None
    order_approved_at: datetime | None = None
    order_delivered_carrier_date: datetime | None = None
    order_delivered_customer_date: datetime | None = None
    order_estimated_delivery_date: datetime | None = None

    class Config:
        from_attributes = True

class OrderItemResponse(BaseModel):
    order_id: str
    order_item_id: int
    product_id: str
    seller_id: str
    shipping_limit_date: datetime
    price: Decimal
    freight_value: Decimal

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    order_id: str
    payment_sequential: int
    payment_type: str
    payment_installments: int
    payment_value: Decimal

    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    review_id: str
    order_id: str
    review_score: int
    review_comment_title: str | None = None
    review_comment_message: str | None = None
    review_creation_date: datetime | None = None
    review_answer_timestamp: datetime | None = None

    class Config:
        from_attributes = True

class CustomerResponse(BaseModel):
    customer_id: str
    customer_unique_id: str
    customer_zip_code_prefix: str
    customer_city: str
    customer_state: str

    class Config:
        from_attributes = True

class OrderDetailResponse(BaseModel):
    order: OrderResponse
    customer: CustomerResponse
    items: list[OrderItemResponse]
    payments: list[PaymentResponse]
    reviews: ReviewResponse | None = None
