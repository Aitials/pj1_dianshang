from sqlalchemy import select ,func ,distinct
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_payments import OrderPayment


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

def get_order_status_distribution(db: Session):
    stmt = (
        select(Order.order_status, func.count(Order.order_id))
        .group_by(Order.order_status)
        .order_by(func.count(Order.order_id).desc())
    )
    return {"items": [{"status": r[0], "count": r[1]} for r in db.execute(stmt).all()]}

def get_order_monthly_trend(db: Session):
    stmt = (
        select(
            func.date_format(Order.order_purchase_timestamp, "%Y-%m").label("month"),
            func.count(distinct(Order.order_id)).label("order_count"),
            func.sum(OrderPayment.payment_value).label("sales"),
        )
        .outerjoin(OrderPayment, OrderPayment.order_id == Order.order_id)
        .where(Order.order_status != "canceled")
        .group_by("month")
        .order_by("month")
    )
    return {"items": [
        {"month": r[0], "order_count": r[1], "sales": round(float(r[2] or 0), 2)}
        for r in db.execute(stmt).all()
    ]}