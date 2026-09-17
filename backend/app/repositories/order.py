from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.order import Order



def get_orders(db: Session, page, page_size, order_status=None ,start_time=None,end_time=None):
    stmt = select(Order)

    if order_status:
        stmt = stmt.where(Order.order_status == order_status)

    if start_time is not None:
        stmt = stmt.where(Order.order_purchase_timestamp >= start_time)

    if end_time is not None:
        stmt = stmt.where(Order.order_purchase_timestamp <= end_time)

    stmt = stmt.limit(page_size).offset((page - 1) * page_size)

    result = db.execute(stmt)
    return result.scalars().all()

def get_order_details(db : Session, order_id :str):
    order = select(Order).where(Order.order_id == order_id)
    result = db.execute(order)
    return result.scalar_one_or_none()