from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.api.deps import require_permission
from app.schemas.AI import AIResponse,AIRequest
from app.services.AI import chat
router = APIRouter()
from app.core.response import ok
from app.schemas.response import ApiResponse

@router.post("/chat" ,response_model=ApiResponse[AIResponse] , dependencies=[Depends(require_permission("ai:chat"))])
def talk(message: AIRequest , current_user=Depends(get_current_user)):
    return ok(chat(message.message , current_user.id , message.thread_id ))