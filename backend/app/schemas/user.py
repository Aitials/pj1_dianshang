from pydantic import BaseModel


class CreateUser(BaseModel):
    username: str
    password: str

class UpdateUser(BaseModel):
    password: str