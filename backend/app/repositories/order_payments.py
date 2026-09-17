from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order_payments import OrderPayment


def get_order_payments(db: Session, page: int, page_size: int):
    stmt = select(OrderPayment).limit(page_size).offset((page - 1) * page_size)
    result = db.execute(stmt)
    return result.scalars().all()

def get_payments_byid(db: Session, order_id: str):
    stmt = select(OrderPayment).where(OrderPayment.order_id == order_id)
    result = db.execute(stmt).scalars().all()
    return result