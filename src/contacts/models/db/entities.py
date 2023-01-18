from pydantic import BaseModel


class UserInDb(BaseModel):
    id: int
    username: str
    hashed_password: str
    role: str
