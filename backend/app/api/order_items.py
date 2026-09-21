from fastapi import APIRouter, Depends ,Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.repositories.order_items import get_order_items

router = APIRouter()

@router.get("/order_items" ,dependencies=[Depends(require_permission("order:read"))])
def list_order_items(db: Session = Depends(get_db),page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100)):
    orderitems = get_order_items(db,page,page_size)
    return {
        "items" : [
            {"order_id" : oi.order_id,
             "order_item_id" : oi.order_item_id,
             "product_id" : oi.product_id,
             "seller_id" : oi.seller_id,
             "shipping_limit_date" : oi.shipping_limit_date,
             "price" : oi.price,
             "freight_value" : oi.freight_value,
             }
            for oi in orderitems
        ]
    }
