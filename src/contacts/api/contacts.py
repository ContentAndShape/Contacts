import uuid

from fastapi import APIRouter, Response, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert

from contacts.models.schemas.contacts import (
    BaseContact,
    ContactInCreate,
    ContactInGet,
    ContactInUpdate,
    ContactInDelete,
    ContactInResponse,
)
from contacts.models.db.tables import Contact
from .dependencies.db import get_session
from .dependencies.api import get_token
from contacts.helpers.contacts import phone_number_is_valid, user_has_contact
from contacts.helpers.security import validate_jwt


router = APIRouter()


@router.post("/", response_model=ContactInResponse)
async def create_contact(
    request_contact: ContactInCreate,
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_session),
    token: str | None = Depends(get_token),
) -> ContactInResponse:
    if token is None:
        raise HTTPException(status_code=400, detail="No token provided")

    valid_res = validate_jwt(token=token, secret=request.app.state.secret)

    if valid_res["status_code"] != 200:
        raise HTTPException(
            status_code=valid_res["status_code"], 
            detail=valid_res["detail"],
        )

    if not phone_number_is_valid(phone_number=request_contact.phone_number):
        raise HTTPException(status_code=422, detail="invalid phone number")

    payload = valid_res["payload"]

    if await user_has_contact(
        user_id=int(payload["id"]),
        phone_number=request_contact.phone_number,
        session=session,
    ):
        raise HTTPException(status_code=409, detail=f"phone number already exist")

    contact_id = str(uuid.uuid4())

    async with session.begin():
        stmt = (
            insert(Contact).
            values(
                id=contact_id,
                owner_id=int(payload["id"]),
                last_name=request_contact.last_name,
                first_name=request_contact.first_name,
                middle_name=request_contact.middle_name,
                organisation=request_contact.organisation,
                job_title=request_contact.job_title,
                email=request_contact.email,
                phone_number=request_contact.phone_number,
            )
        )
        await session.execute(stmt)

    async with session.begin():
        stmt = (
            select(Contact).where(Contact.id == contact_id)
        )
        contact = await session.scalar(stmt)
        contact = BaseContact(
                id=contact_id,
                phone_number=contact.phone_number,
                last_name=contact.last_name,
                first_name=contact.last_name,
                middle_name=contact.middle_name,
            )

    return ContactInResponse(contact=contact)
