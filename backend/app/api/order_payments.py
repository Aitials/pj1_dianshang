from fastapi import APIRouter, Depends ,Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.repositories.order_payments import get_order_payments

router = APIRouter()


@router.get("/payments" ,dependencies=[Depends(require_permission("order:read"))])
def list_order_payments(db: Session = Depends(get_db),page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100)):
    payments = get_order_payments(db, page, page_size)
    return {
        "items": [
            {
                "order_id": p.order_id,
                "payment_sequential": p.payment_sequential,
                "payment_type": p.payment_type,
                "payment_installments": p.payment_installments,
                "payment_value": p.payment_value,
            }
            for p in payments
        ]
    }
