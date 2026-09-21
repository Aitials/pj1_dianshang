from sqlalchemy.orm import Session

from app.repositories.customer import get_customer_repurchase


def get_customer_repurchase_info(db: Session):
    return get_customer_repurchase(db)
