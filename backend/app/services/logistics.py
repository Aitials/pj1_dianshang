from sqlalchemy.orm import Session

from app.repositories.logistics import get_logistics_overview


def get_logistics(db: Session):
    return get_logistics_overview(db)
