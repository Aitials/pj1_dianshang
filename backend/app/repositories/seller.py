from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.seller import Seller


def get_sellers(db: Session, limit: int = 20):
    stmt = select(Seller).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()
