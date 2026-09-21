from sqlalchemy.orm import Session

from app.services.customer import get_customer_repurchase_info


def query_customer(db: Session):
    return get_customer_repurchase_info(db)
