from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import func

from app.db.session import Base


class OperationLog(Base):
    __tablename__ = "operation_log"

    id = Column(Integer, primary_key=True, nullable=False)
    operator = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    target = Column(String(100), nullable=True)
    detail = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
