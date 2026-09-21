from sqlalchemy.orm import Session

from app.services.order import get_order_status


def query_order_status(db: Session):
    return get_order_status(db)
