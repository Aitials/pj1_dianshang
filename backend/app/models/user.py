from sqlalchemy import Column, Integer, String
from app.db.session import Base

class User(Base):
    __tablename__ = "system_user"
    id = Column(Integer, primary_key=True)
    username = Column(String(50),nullable=False,unique=True)
    password_hash = Column(String(50),nullable=False)