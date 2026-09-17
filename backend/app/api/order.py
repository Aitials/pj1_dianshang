from fastapi import APIRouter ,Depends
from app.db.session import get_db
from app.repositories.order import get_orders
from app.repositories.dashboard import count_orders
from sqlalchemy.orm import Session
router = APIRouter()
@router.get("/orders")
def list_orders(db : Session = Depends(get_db),page: int =1,page_size: int =20):
    orders= get_orders(db,page,page_size)
    counts = count_orders(db)
    return {
        "total": counts,
        "page" : page,
        "page_size" : page_size,
        "items":[
            {
            "order_id" : o.order_id,
            "customer_id" : o.customer_id,
            "order_status" : o.order_status,
            "order_purchase_timestamp" : o.order_purchase_timestamp,
            "order_approved_at" : o.order_approved_at,
            "order_delivered_carrier_date" : o.order_delivered_carrier_date,
            "order_delivered_customer_date" : o.order_delivered_customer_date,
            "order_estimated_delivery_date" : o.order_estimated_delivery_date,
            }
            for o in orders
        ]
    }