import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class PayloadData(BaseModel):
    sub: int
    role: str
    exp: datetime.datetime | None = None
