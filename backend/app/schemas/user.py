from pydantic import BaseModel


class CreateUser(BaseModel):
    username: str
    password: str

class UpdateUser(BaseModel):
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

class Role(BaseModel):
    id: int
    name: str
    description: str |None = None

class RoleListResponse(BaseModel):
    roles: list[Role]

class AssignRole(BaseModel):
    role_ids: list[int]

class AssignRoleResponse(BaseModel):
    user_id: int
    role_ids: list[int]

