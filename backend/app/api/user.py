from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import CreateUser ,UpdateUser
from app.db.session import get_db
from app.repositories.user import get_users, get_user_by_id ,create_user ,get_user ,update_user_password
from app.api.deps import require_permission
from app.core.security import hash_password

router = APIRouter()


@router.get("/users",dependencies=[Depends(require_permission("user:read"))])
def list_users(page: int = 1,page_size: int = 20,db: Session = Depends(get_db),):
    users = get_users(db, page, page_size)
    return {
        "items": [
            {
                "id": user.id,
                "username": user.username,
            }
            for user in users
        ]
    }

@router.get("/users/{user_id}",dependencies=[Depends(require_permission("user:read"))])
def get_user_detail(user_id: int,db: Session = Depends(get_db),):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "username": user.username,
    }

@router.post("/users",dependencies=[Depends(require_permission("user:create"))])
def create_system_user(body: CreateUser,db: Session = Depends(get_db),):
    if get_user(db, body.username) is not None:
        raise HTTPException(
            status_code=400,
            detail="用户名已被占用"
        )

    user = create_user(
        db,
        body.username,
        hash_password(body.password),
    )

    return {
        "id": user.id,
        "username": user.username,
    }

@router.put("/users/{user_id}",dependencies=[Depends(require_permission("user:update"))])
def update_user(user_id: int,body: UpdateUser,db: Session = Depends(get_db),):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    update_user_password(db,user,hash_password(body.password))

    return {
        "id": user.id,
        "username": user.username,
        "message": "密码修改成功",
    }