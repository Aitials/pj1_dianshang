from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.products import Products

def get_products(db: Session, limit : int=20):
    stmt = select(Products).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()



