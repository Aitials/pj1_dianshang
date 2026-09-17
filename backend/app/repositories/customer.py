from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.customer import Customer

def get_customers(db : Session, limit:int = 20):
    stmt = select(Customer).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


