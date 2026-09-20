from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from datetime import datetime
from app.core.response import ApiResponse, ok ,ok_page
from app.repositories.order import get_orders ,get_order_details ,get_order_status_distribution ,get_order_monthly_trend
from app.repositories.order_items import get_orderitemd_byid
from app.repositories.order_payments import get_payments_byid
from app.repositories.order_reviews import get_reviews_byid
from app.repositories.customer import get_customer_by_id
from app.repositories.dashboard import count_orders
from app.schemas.order import OrderDetailResponse, OrderResponse
from sqlalchemy.orm import Session
from app.api.deps import require_permission
from app.schemas.response import PageData

router = APIRouter()
@router.get("/orders" ,response_model=ApiResponse[PageData[OrderResponse]],dependencies=[Depends(require_permission("order:read"))])
def list_orders(db : Session = Depends(get_db),page: int =1,page_size: int =20 , order_status: str | None = None ,start_time: datetime | None = None, end_time: datetime | None = None):
    orders= get_orders(db,page,page_size ,order_status , start_time, end_time)
    counts = count_orders(db ,order_status , start_time, end_time)
    items = [
        {
            "order_id": o.order_id,
            "customer_id": o.customer_id,
            "order_status": o.order_status,
            "order_purchase_timestamp": o.order_purchase_timestamp,
            "order_approved_at":o.order_approved_at,
            "order_delivered_carrier_date": o.order_delivered_carrier_date,
            "order_delivered_customer_date": o.order_delivered_customer_date,
            "order_estimated_delivery_date": o.order_estimated_delivery_date,
        }
        for o in orders
    ]
    return ok_page(items,counts ,page,page_size)

@router.get("/orders/status-distribution", response_model=ApiResponse[dict], dependencies=[Depends(require_permission("order:read"))])
def order_status_distribution(db: Session = Depends(get_db)):
    return ok(get_order_status_distribution(db))

@router.get("/orders/monthly-trend", response_model=ApiResponse[dict], dependencies=[Depends(require_permission("order:read"))])
def order_monthly_trend(db: Session = Depends(get_db)):
    return ok(get_order_monthly_trend(db))

@router.get("/orders/{order_id}", response_model=ApiResponse[OrderDetailResponse] ,dependencies=[Depends(require_permission("order:read"))])
def get_order_detail(order_id:str,db: Session = Depends(get_db),):
    order_detail = get_order_details(db,order_id)
    if order_detail is None:
        raise HTTPException(status_code=404, detail="Order not found")
    orderitems = get_orderitemd_byid(db,order_id)
    payment = get_payments_byid(db,order_id)
    reviews = get_reviews_byid(db,order_id)
    customer = get_customer_by_id(db,order_detail.customer_id)
    detail = OrderDetailResponse.model_validate({
        "order": order_detail,
        "customer": customer,
        "items": orderitems,
        "payments": payment,
        "reviews": reviews,
    })
    return ok(detail)
