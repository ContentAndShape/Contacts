from fastapi import Request
from pydantic import EmailStr

from contacts.models.schemas.contacts import FilterParams


def get_token(request: Request) -> str | None:
    try:
        token = request.cookies["token"]
    except KeyError:
        return None

    return token


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
