from fastapi import APIRouter, Depends ,HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import ApiResponse, ok
from app.schemas.user import CreateUser, UpdateUser, UserResponse ,RoleListResponse ,AssignRole ,AssignRoleResponse
from app.repositories.user import get_users, get_user_by_id ,create_user ,get_user ,update_user_password ,put_user_role ,get_role
from app.api.deps import require_permission, get_current_user
from app.repositories.operation_log import create_log
from app.core.security import hash_password

router = APIRouter()


@router.get("/users",response_model=ApiResponse[list[UserResponse]],dependencies=[Depends(require_permission("user:read"))])
def list_users(page: int = 1,page_size: int = 20,db: Session = Depends(get_db),):
    users = get_users(db, page, page_size)
    return ok([
            {
                "id": user.id,
                "username": user.username,
            }
            for user in users])

@router.get("/users/{user_id}",response_model=ApiResponse[UserResponse],dependencies=[Depends(require_permission("user:read"))])
def get_user_detail(user_id: int,db: Session = Depends(get_db),):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return ok({
        "id": user.id,
        "username": user.username,
    })

@router.post("/users",response_model=ApiResponse[UserResponse],dependencies=[Depends(require_permission("user:create"))])
def create_system_user(body: CreateUser,db: Session = Depends(get_db),current_user=Depends(get_current_user)):
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

    create_log(db, current_user.username, "create_user", str(user.id), f"username={body.username}")

    return ok({
        "id": user.id,
        "username": user.username,
    })

@router.get('/roles'  ,response_model=ApiResponse[RoleListResponse], dependencies=[Depends(require_permission("user:read"))])
def list_role(db: Session = Depends(get_db)):
    roles = get_role(db)
    return ok(roles)


@router.put("/users/{user_id}",response_model=ApiResponse[UserResponse],dependencies=[Depends(require_permission("user:update"))])
def update_user(user_id: int,body: UpdateUser,db: Session = Depends(get_db),):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    update_user_password(db,user,hash_password(body.password))

    return ok({
        "id": user.id,
        "username": user.username,
    },message= "密码修改成功")

@router.put('/users/{user_id}/roles', response_model=ApiResponse[AssignRoleResponse], dependencies=[Depends(require_permission("user:update"))])
def assign_role(user_id: int, body: AssignRole, db:Session = Depends(get_db), current_user=Depends(get_current_user)):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(404, "User not found")
    result = put_user_role(user_id, body.role_ids, db)
    create_log(db, current_user.username, "assign_role", str(user_id), f"role_ids={body.role_ids}")
    return ok(result)
