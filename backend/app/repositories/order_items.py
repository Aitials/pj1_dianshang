from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.order_items import OrderItem

def get_order_items(db: Session ,page, page_size):
    stmt = select(OrderItem).limit(page_size).offset((page -1)*page_size)
    result = db.execute(stmt)
    return result.scalars().all()

def get_orderitemd_byid(db: Session ,order_id: str):
    stmt = select(OrderItem).where(OrderItem.order_id == order_id)
    return db.execute(stmt).scalars().all()