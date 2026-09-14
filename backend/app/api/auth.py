from fastapi import APIRouter
from app.schemas.auth import LoginUser
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.auth import LoginUser
from app.db.session import get_db
from app.services.auth import authenticate_user
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
        return {
            "message": "用户名或密码错误"
        }

    return {
        "message": "登录成功",
        "username": current_user.username
    }