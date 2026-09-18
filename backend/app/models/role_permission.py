from sqlalchemy import Column, Integer, ForeignKey

from app.db.session import Base


class RolePermission(Base):
    __tablename__ = "system_role_permission"

    id = Column(Integer, primary_key=True)

    role_id = Column(
        Integer,
        ForeignKey("system_role.id"),
        nullable=False
    )

    permission_id = Column(
        Integer,
        ForeignKey("system_permission.id"),
        nullable=False
    )