from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.order_payments import get_order_payments

router = APIRouter()


@router.get("/payments")
def list_order_payments(db: Session = Depends(get_db), page: int = 1, page_size: int = 20):
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
