import logging

from fastapi import Depends, HTTPException ,Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.repositories.permission import get_user_permissions
from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user import get_user

logger = logging.getLogger("app.api.deps")

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
    except Exception as e:
        # 记日志而不是静默：裸 except 会把「SECRET_KEY 没配」这类配置错误
        # 也伪装成「token 无效」，配错了却以为是 token 问题，很难查。
        logger.warning("token 解析失败：%s", e)
        raise HTTPException(status_code=401, detail="token 无效或已过期")

    user = get_user(db, username)
    if user is None:
        # 这里**刻意不用 401**：token 本身是有效的，只是用户查不到（账号被删/停用）。
        # 前端把所有 401 当作「登录过期」处理 —— 清空登录态并强制跳登录页，
        # 用户只会看到一句"用户不存在"然后被静默登出，难以理解原因。
        # 改用 403：前端只弹提示，由用户自己决定下一步，语义也更准确
        # （凭证可信，但服务器拒绝为该主体授权）。
        raise HTTPException(status_code=403, detail="账号不存在或已被停用")

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