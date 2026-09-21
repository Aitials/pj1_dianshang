from sqlalchemy.orm import Session

from app.repositories.order import get_order_status_distribution


def get_order_status(db: Session):
    return get_order_status_distribution(db)
