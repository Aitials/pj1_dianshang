from sqlalchemy.orm import Session

from app.services.logistics import get_logistics


def query_logistics(db: Session):
    return get_logistics(db)
