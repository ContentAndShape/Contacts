import uuid
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class BaseContact(BaseModel):
    last_name: str
    first_name: str
    middle_name: str
    organisation: Optional[str]
    job_title: Optional[str]
    email: EmailStr
    phone_number: str


class ContactWithId(BaseContact):
    id: uuid.UUID


class ContactInCreate(BaseModel):
    last_name: str
    first_name: str
    middle_name: str
    organisation: str
    job_title: str
    email: EmailStr
    phone_number: str   


class ContactInUpdate(BaseModel):
    id: uuid.UUID
    owner_id: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    job_title: Optional[str]
    organisation: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]


class ContactInDelete(BaseModel):
    id: uuid.UUID


class ContactInResponse(BaseModel):
    contact: ContactWithId


class ContactsInResponse(BaseModel):
    contacts: List[BaseContact]
