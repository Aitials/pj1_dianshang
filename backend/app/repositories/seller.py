from sqlalchemy import select ,func
from sqlalchemy.orm import Session

from app.models.seller import Seller


def get_sellers(page ,page_size,seller_city,seller_state,db: Session):
    stmt = select(Seller)
    if seller_city is not None:
        stmt = stmt.where(Seller.seller_city == seller_city)
    if seller_state is not None:
        stmt = stmt.where(Seller.seller_state == seller_state)
    stmt = stmt.limit(page_size).offset((page -1 ) * page_size)
    result = db.execute(stmt)
    return result.scalars().all()

def get_seller_byid(db: Session, seller_id: str):
    stmt = select(Seller).where(Seller.seller_id == seller_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def count_sellers(seller_city,seller_state,db: Session):
    stmt = select(func.count(Seller.seller_id))
    if seller_city is not None:
        stmt = stmt.where(Seller.seller_city == seller_city)
    if seller_state is not None:
        stmt = stmt.where(Seller.seller_state == seller_state)
    result = db.execute(stmt).scalar()
    return result