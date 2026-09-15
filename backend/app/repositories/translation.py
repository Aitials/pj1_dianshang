from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.translation import Translation


def get_translations(db: Session):
    stmt = select(Translation)
    result = db.execute(stmt)
    return result.scalars().all()
