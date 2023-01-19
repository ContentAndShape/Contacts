import jwt

from fastapi import Request, HTTPException
from pydantic import EmailStr
from loguru import logger

from contacts.helpers.security import ALGORITHM, validate_jwt
from contacts.models.schemas.contacts import BaseContact, FilterParams


# def get_token_from_cookies(cookies: dict) -> str | None:
#     try:
#         token = cookies["token"]
#     except KeyError:
#         token = None
# 
#     return token


def get_token_from_headers(headers: dict) -> str | None:
    try:
        token = headers["access_token"]
    except KeyError:
        token = None

    return token


def get_payload_from_jwt(request: Request) -> dict:
    # token = get_token_from_cookies(request.cookies)
    token = get_token_from_headers(headers=request.headers)
    secret = request.app.state.secret

    return jwt.decode(token, secret, algorithms=[ALGORITHM])


def verify_jwt(request: Request) -> None:
    # token = get_token_from_cookies(request.cookies)
    token = get_token_from_headers(headers=request.headers)

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
) -> FilterParams:
    return FilterParams(
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
