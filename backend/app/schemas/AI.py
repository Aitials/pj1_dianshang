from pydantic import BaseModel


class AIRequest(BaseModel):
    message : str

class AIResponse(BaseModel):
    answer : str