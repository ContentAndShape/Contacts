from pydantic import BaseModel

from .meta import UserRoleEnum


class BaseUser(BaseModel):
    id: int
    role: UserRoleEnum

    class Config:
        use_enum_values = True


class UserInResponse(BaseModel):
    user: BaseUser


class UserInCreate(BaseUser):
    username: str
    password: str


class UserInLogin(BaseModel):
    username: str
    password: str
