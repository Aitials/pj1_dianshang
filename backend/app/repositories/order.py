from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.order import Order
from sqlalchemy import func


def get_orders(db : Session,page, page_size):
    stmt = select(Order).limit(page_size).offset((page-1) * page_size)
    result = db.execute(stmt)
    return result.scalars().all()

def count_orders(db : Session):
    stmt = select(func.count(Order.order_id))
    counts = db.execute(stmt)
    return counts.scalars().one()