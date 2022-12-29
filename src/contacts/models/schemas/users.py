from enum import Enum

from pydantic import BaseModel


class RoleEnum(str, Enum):
    admin = 'admin'
    user = 'user'


class BaseUser(BaseModel):
    id: str
    role: RoleEnum

    class Config:
        use_enum_values = True


class UserInResponse(BaseModel):
    user: BaseUser


class UserInCreate(BaseUser):
    password: str


class UserInLogin(BaseModel):
    username: str
    password: str
