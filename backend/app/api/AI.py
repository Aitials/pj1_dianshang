from fastapi import APIRouter, Depends
from app.schemas.AI import AIResponse,AIRequest
from app.services.AI import chat
from sqlalchemy.orm import Session
from app.db.session import get_db
router = APIRouter()
from app.core.response import ok, ok_page
from app.schemas.response import ApiResponse, PageData

@router.post("/chat" ,response_model=ApiResponse[AIResponse])
def talk(message: AIRequest , db: Session = Depends(get_db)):
    return ok({"answer":chat(message.message ,db)})