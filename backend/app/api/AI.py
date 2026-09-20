from fastapi import APIRouter, Depends
from app.schemas.AI import AIResponse,AIRequest
from app.services.AI import chat
from sqlalchemy.orm import Session
from app.db.session import get_db
router = APIRouter()


@router.post("/chat" ,response_model=AIResponse)
def talk(message: AIRequest , db: Session = Depends(get_db)):
    return {"answer":chat(message.message ,db)}