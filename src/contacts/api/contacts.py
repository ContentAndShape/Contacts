import uuid

from loguru import logger
from fastapi import APIRouter, Response, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, and_
from sqlalchemy.engine import ChunkedIteratorResult

from contacts.models.schemas.contacts import (
    BaseContact,
    ContactWithId,
    ContactInCreate,
    FilterParams,
    ContactInUpdate,
    ContactInDelete,
    ContactInResponse,
    ContactsInResponse
)
from contacts.models.db.tables import Contact
from .dependencies.db import get_session
from .dependencies.api import get_token, get_filter_params
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
        raise HTTPException(status_code=422, detail="invalid phone number fromat")

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
        contact = ContactInResponse(
            contact=ContactWithId(
                id=contact_id,
                last_name=contact.last_name,
                first_name=contact.last_name,
                middle_name=contact.middle_name,
                organisation=contact.organisation,
                job_title=contact.job_title,
                email=contact.email,
                phone_number=contact.phone_number,
            )
        )

    return contact


@router.get("/", response_model=ContactsInResponse)
async def get_contacts(
    request: Request,
    response: Response,
    order_by: str = "last_name",
    filter_params: FilterParams = Depends(get_filter_params),
    session: AsyncSession = Depends(get_session),
    token: str | None = Depends(get_token),
) -> ContactsInResponse:
    if token is None:
        raise HTTPException(status_code=400, detail="No token provided")

    valid_res = validate_jwt(token=token, secret=request.app.state.secret)

    if valid_res["status_code"] != 200:
        raise HTTPException(
            status_code=valid_res["status_code"], 
            detail=valid_res["detail"],
        )
    
    payload = valid_res["payload"]
    user_id = int(payload["id"])

    async with session.begin():
        # Get only user-owned contacts
        if payload["role"] == "user":
            stmt = (
                select(Contact).
                filter_by(
                    owner_id = user_id, 
                    **filter_params.dict(exclude_none=True),
                )
            )

        if payload["role"] == "admin":
            stmt = (
                select(Contact).
                filter_by(**filter_params.dict(exclude_none=True))
            )

        stmt = stmt.order_by(order_by)
        result: ChunkedIteratorResult = await session.execute(stmt)

        contacts = ContactsInResponse(
            contacts=[BaseContact(
                first_name=contact.first_name,
                last_name=contact.last_name,
                middle_name=contact.middle_name,
                organisation=contact.organisation,
                job_title=contact.job_title,
                email=contact.email,
                phone_number=contact.phone_number,
            ) for contact in result.scalars().all()],
        )

    return contacts
