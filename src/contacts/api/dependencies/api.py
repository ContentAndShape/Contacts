import jwt

from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from loguru import logger

from contacts.models.schemas.auth import Token, PayloadData
from contacts.helpers.security import ALGORITHM, validate_jwt
from contacts.models.schemas.contacts import BaseContact
from contacts.models.schemas.meta import ContactsFilterParams


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
)


def get_payload_from_jwt(request: Request, token: str = Depends(oauth2_scheme)) -> PayloadData:
    payload = jwt.decode(token, request.app.state.secret, algorithms=[ALGORITHM])
    return PayloadData(**payload)


def process_jwt(request: Request, token: Token = Depends(oauth2_scheme)) -> None:
    """Entrypoint for token processing"""
    if token is None:
        raise HTTPException(status_code=400, detail="no token provided")
    validate_jwt(token, request.app.state.secret)


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
        raise HTTPException(status_code=422, detail="invalid phone number length")
    
    for char in request_contact.phone_number:
        try:
            int(char)
        except ValueError:
            raise HTTPException(status_code=422, detail="invalid phone number format")
