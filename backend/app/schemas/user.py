from pydantic import BaseModel


class CreateUser(BaseModel):
    username: str
    password: str

class UpdateUser(BaseModel):
    password: str

class UserResponse(BaseModel):
    id: int
    username: str