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
    id: str


class ContactInCreate(BaseModel):
    last_name: str
    first_name: str
    middle_name: str
    organisation: str
    job_title: str
    email: EmailStr
    phone_number: str


class FilterParams(BaseModel):
    owner_id: Optional[int]
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    job_title: Optional[str]
    organisation: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]    


class ContactInUpdate(BaseModel):
    id: str
    owner_id: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    job_title: Optional[str]
    organisation: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]


class ContactInDelete(BaseModel):
    id: str


class ContactInResponse(BaseModel):
    contact: ContactWithId


class ContactsInResponse(BaseModel):
    contacts: List[BaseContact]
