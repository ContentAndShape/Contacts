from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRoleEnum(str, Enum):
    admin = 'admin'
    user = 'user'


class OrderContactsByEnum(str, Enum):
    last_name = 'last_name'
    first_name = 'first_name'
    middle_name = 'middle_name'
    job_title = 'job_title'
    organisation = 'organisation'
    email = 'email'
    phone_number = 'phone_number'


class ContactsFilterParams(BaseModel):
    owner_id: Optional[int]
    last_name: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    job_title: Optional[str]
    organisation: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
