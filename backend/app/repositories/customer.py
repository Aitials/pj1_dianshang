from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.customer import Customer

def get_customers(db : Session, limit:int = 20):
    stmt = select(Customer).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()

def get_customer_by_id(db: Session, customer_id: str):
    stmt = select(Customer).where(Customer.customer_id == customer_id)
    result = db.execute(stmt).scalar_one_or_none()
    return result
