import jwt

from loguru import logger
from fastapi import Request, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from contacts.helpers.security import ALGORITHM, validate_jwt
from contacts.helpers.contacts import contact_is_owned_by_user
from .db import get_session
from contacts.db.crud.users import get_user
from contacts.db.crud.contacts import get_contact
from contacts.models.schemas.auth import Token, PayloadData
from contacts.models.schemas.meta import UserRoleEnum, ContactsFilterParams
from contacts.models.schemas.contacts import BaseContact
from contacts.models.schemas.users import UserInCreate
from contacts.resources.errors.users import (
    USERNAME_EXIST_EXCEPTION,
    USER_ID_EXIST_EXCEPTION,
    USER_CONTACT_OWNERSHIP_EXCEPTION,
)
from contacts.resources.errors.contacts import (
    CONTACT_DOES_NOT_EXIST_EXCEPTION,
    PHONE_NUM_FORMAT_EXCEPTION,
    PHONE_NUM_LEN_EXCEPTION,
)
from contacts.resources.errors.auth import (
    NO_TOKEN_EXCEPTION,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
)


def get_payload_from_jwt(request: Request, token: str = Depends(oauth2_scheme)) -> PayloadData:
    payload = jwt.decode(token, request.app.state.secret, algorithms=[ALGORITHM])
    return PayloadData(**payload)


def process_jwt(request: Request, token: Token = Depends(oauth2_scheme)) -> None:
    """Entrypoint for token processing"""
    if token is None:
        raise NO_TOKEN_EXCEPTION
    validate_jwt(token, request.app.state.secret)


async def validate_contact_ownership(
    contact_id: str,
    payload: PayloadData = Depends(get_payload_from_jwt), 
    db_session: AsyncSession = Depends(get_session),
) -> None:
    """Checks if user has rights to interact with requested contact"""
    if payload.role == UserRoleEnum.admin.value:
        return
    
    if payload.role == UserRoleEnum.user.value:
        if not await contact_is_owned_by_user(
            contact_id=contact_id, 
            user_id=payload.sub, 
            session=db_session
        ):
            raise USER_CONTACT_OWNERSHIP_EXCEPTION


def get_filter_params(
    owner_id: int | None = None,
    last_name: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
    job_title: str | None = None,
    organisation: str | None = None,
    email: EmailStr | None = None,
    phone_number: str | None = None,
) -> ContactsFilterParams:
    return ContactsFilterParams(
        owner_id=owner_id,
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        job_title=job_title,
        organisation=organisation,
        email=email,
        phone_number=phone_number,
    )


def validate_phone_number(request_contact: BaseContact) -> None:
    if len(request_contact.phone_number) != 11:
        raise PHONE_NUM_LEN_EXCEPTION
    
    try:
        int(request_contact.phone_number)
    except ValueError:
        raise PHONE_NUM_FORMAT_EXCEPTION


async def check_contact_existence(contact_id: str, db_sesion = Depends(get_session)) -> None:
    contact = await get_contact(id=contact_id, db_session=db_sesion)
    if contact is None:
        raise CONTACT_DOES_NOT_EXIST_EXCEPTION


async def check_user_uniqueness(
    user: UserInCreate, 
    session: AsyncSession = Depends(get_session)
) -> None:
    user_db = await get_user(username=user.username, session=session)
    if user_db:
        raise USERNAME_EXIST_EXCEPTION
    user_db = await get_user(id=user.id, session=session)
    if user_db:
        raise USER_ID_EXIST_EXCEPTION
