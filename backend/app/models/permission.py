from sqlalchemy import Column, Integer, String

from app.db.session import Base


class Permission(Base):
    __tablename__ = "system_permission"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)