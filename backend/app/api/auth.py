from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.auth import LoginUser
from app.db.session import get_db
from app.services.auth import authenticate_user
from app.core.security import create_access_token

router = APIRouter()


@router.post("/login")
def login(
    user: LoginUser,
    db: Session = Depends(get_db)
):
    current_user = authenticate_user(
        db,
        user.username,
        user.password
    )

    if current_user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(current_user.username)

    return {
        "message": "登录成功",
        "username": current_user.username,
        "access_token": token,
        "token_type": "bearer"
    }
