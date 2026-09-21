from sqlalchemy.orm import Session

from app.repositories.inventory import get_warnings


def get_inventory_warning(db: Session):
    return get_warnings(db)
