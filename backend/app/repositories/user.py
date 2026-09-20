from sqlalchemy import select ,delete
from sqlalchemy.orm import Session
from app.models.user_role import UserRole
from app.models.user import User
from app.models.role import Role


def get_user(db: Session, username: str):
    stmt = select(User).where(User.username == username)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def create_user(db: Session, username: str, password_hash: str):
    user = User(username=username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session, page: int, page_size: int):
    stmt = (
        select(User)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = db.execute(stmt)
    return result.scalars().all()

def get_user_by_id(db: Session, user_id: int):
    stmt = select(User).where(User.id == user_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def update_user_password(db: Session,user: User,password_hash: str,):
    user.password_hash = password_hash
    db.commit()
    db.refresh(user)
    return user

def get_role(db : Session):
    stmt = select(Role.id, Role.name, Role.description)
    result = db.execute(stmt).all()
    return {
        "roles" : [
            {
                "id": i.id,
                "name" : i.name,
                "description" : i.description
            }
            for i in result
        ]
    }

def put_user_role(user_id,role_ids,db: Session):
    db.execute(delete(UserRole).where(UserRole.user_id == user_id))
    for rid in role_ids:
        db.add(UserRole(user_id=user_id, role_id=rid))
    db.commit()
    return {"user_id": user_id, "role_ids": role_ids}
