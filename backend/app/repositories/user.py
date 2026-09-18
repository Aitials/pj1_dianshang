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

def get_users(db: Session, page: int, page_size: int):
    stmt = (
        select(User)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = db.execute(stmt)
    return result.scalars().all()

def get_user_by_id(db: Session, user_id: int):
    stmt = select(User).where(User.id == user_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def update_user_password(db: Session,user: User,password_hash: str,):
    user.password_hash = password_hash
    db.commit()
    db.refresh(user)
    return user

