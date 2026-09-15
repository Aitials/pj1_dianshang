from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user(db: Session, username: str):
    stmt = select(User).where(User.username == username)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def create_user(db: Session, username: str, password_hash: str):
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
