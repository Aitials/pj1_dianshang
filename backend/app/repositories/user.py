from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user(db: Session, username: str):
    stmt = select(User).where(User.username == username)

    result = db.execute(stmt)

    user = result.scalar_one_or_none()

    return user