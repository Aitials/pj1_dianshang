from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import seller

def get_seller(db: Session,limit :int = 20):
    stmt = select(seller.Sellers).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()