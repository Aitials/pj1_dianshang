from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.repositories.user import create_user, get_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def register_user(db: Session, username: str, password: str):
    if get_user(db, username):
        return None

    return create_user(db, username, hash_password(password))

