from sqlalchemy.orm import Session

from app.services.inventory import get_inventory_warning


def query_inventory_warning(db: Session):
    warning = get_inventory_warning(db)
    return {
        "total": len(warning),
        "items": warning[:15],
    }
