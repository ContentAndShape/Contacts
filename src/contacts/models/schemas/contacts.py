from typing import Optional

from pydantic import BaseModel, EmailStr


class ContactInCreate(BaseModel):
    owner_id: str
    last_name: str
    first_name: str
    middle_name: str
    job_title: str
    email: EmailStr
    phone_number: str


class ContactInGet(BaseModel):
    id: str


class ContactInUpdate(BaseModel):
    id: str
    owner_id: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    job_title: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]


class ContactInDelete(BaseModel):
    id: str
