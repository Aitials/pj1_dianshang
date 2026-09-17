from sqlalchemy import select ,func
from sqlalchemy.orm import Session
from app.models.customer import Customer

def get_customers(page ,page_size,customer_city,customer_state,db : Session):
    stmt = select(Customer)
    if customer_city is not None:
        stmt = stmt.where(Customer.customer_city == customer_city)
    if customer_state is not None:
        stmt = stmt.where(Customer.customer_state == customer_state)
    stmt = stmt.limit(page_size).offset((page -1)*page_size)
    result = db.execute(stmt)
    return result.scalars().all()

def get_customer_by_id(db: Session, customer_id: str):
    stmt = select(Customer).where(Customer.customer_id == customer_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def count_customers(customer_city,customer_state,db: Session):
    stmt =  select(func.count(Customer.customer_id))
    if customer_state is not None:
        stmt = stmt.where(Customer.customer_state == customer_state)
    if customer_city is not None:
        stmt = stmt.where(Customer.customer_city == customer_city)
    result = db.execute(stmt)
    return result.scalar()