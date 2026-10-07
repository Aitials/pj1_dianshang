from pydantic import BaseModel


class AIRequest(BaseModel):
    message : str
    thread_id: str | None = None

class AIResponse(BaseModel):
    answer : str
    thread_id : str