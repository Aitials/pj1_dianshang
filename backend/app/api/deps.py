from fastapi import Depends, HTTPException ,Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.repositories.permission import get_user_permissions
from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user import get_user

security = HTTPBearer()

def page_params(page:int = Query(1,ge =1) ,page_size : int = Query(10 , ge=1, le=100)):
    return {"page": page, "page_size": page_size,
            "offset": (page - 1) * page_size, "limit": page_size}


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

def require_permission(permission_name: str):

    def permission_checker(
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        permissions = get_user_permissions(db, current_user.id)

        if permission_name not in permissions:
            raise HTTPException(
                status_code=403,
                detail="没有权限执行此操作"
            )

        return current_user

    return permission_checker