from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user import get_user

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        username = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="token 无效或已过期")

    user = get_user(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user
