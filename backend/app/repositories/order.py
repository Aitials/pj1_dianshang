from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.order import Order



def get_orders(db : Session,page, page_size):
    stmt = select(Order).limit(page_size).offset((page-1) * page_size)
    result = db.execute(stmt)
    return result.scalars().all()

