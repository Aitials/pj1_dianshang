from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.session import Base


class AiAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=True)
    question = Column(Text, nullable=False)
    tool_context = Column(Text, nullable=True)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())