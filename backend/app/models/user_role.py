from sqlalchemy import Column, Integer, ForeignKey

from app.db.session import Base


class UserRole(Base):
    __tablename__ = "system_user_role"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("system_user.id"),
        nullable=False
    )

    role_id = Column(
        Integer,
        ForeignKey("system_role.id"),
        nullable=False
    )