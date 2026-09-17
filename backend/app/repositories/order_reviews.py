from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order_reviews import OrderReview


def get_order_reviews(db: Session, page: int, page_size: int):
    stmt = select(OrderReview).limit(page_size).offset((page - 1) * page_size)
    result = db.execute(stmt)
    return result.scalars().all()

def get_reviews_byid(db: Session, order_id: str):
    stmt = select(OrderReview).where(OrderReview.order_id == order_id)
    result = db.execute(stmt).scalar_one_or_none()
    return result