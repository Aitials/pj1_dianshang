from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import LoginUser, RegisterUser
from app.services.auth import authenticate_user, register_user

router = APIRouter()


@router.post("/login")
def login(user: LoginUser, db: Session = Depends(get_db)):
    current_user = authenticate_user(db, user.username, user.password)

    if current_user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(current_user.username)

    return {
        "message": "登录成功",
        "username": current_user.username,
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    new_user = register_user(db, user.username, user.password)

    if new_user is None:
        raise HTTPException(status_code=400, detail="用户名已被占用")

    return {"message": "注册成功", "username": new_user.username}

@router.get("/me")
def read_me(current_user=Depends(get_current_user)):
    return {"username": current_user.username}