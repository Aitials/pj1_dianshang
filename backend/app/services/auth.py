from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.repositories.user import get_user


def authenticate_user(
    db: Session,
    username: str,
    password: str
):
    user = get_user(db, username)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None
    return user