from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import LoginUser, RegisterUser
from app.services.auth import authenticate_user, register_user
from app.repositories.permission import get_user_roles

router = APIRouter()


@router.post("/login" ,)
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
def read_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {"username": current_user.username,
            "role" : get_user_roles(db,current_user.id)}


@router.post("/refresh")
def refresh(current_user=Depends(get_current_user)):
    """用当前仍然有效的 token 换一个新 token（滑动续期）。

    刻意保持无状态：不引入 refresh token、不存 Redis、不做吊销。
    代价是**只能在旧 token 尚未过期时使用**——前端在请求发出前检查 exp，
    剩余不足阈值时先调本接口续签、再发原请求。旧 token 一旦真的过期，
    本接口自身也会 401，此时只能重新登录（前端会带 redirect 回跳原页面）。
    """
    return {
        "access_token": create_access_token(current_user.username),
        "token_type": "bearer",
    }
