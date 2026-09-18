from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.models.permission import Permission


def get_user_permissions(db: Session, user_id: int):
    stmt = (
        select(Permission.name)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id
        )
        .join(
            UserRole,
            UserRole.role_id == RolePermission.role_id
        )
        .where(UserRole.user_id == user_id)
    )

    result = db.execute(stmt)
    return result.scalars().all()