from sqlalchemy import Column, Integer, String

from app.db.session import Base


class Role(Base):
    __tablename__ = "system_role"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)