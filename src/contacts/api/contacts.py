import uuid

from loguru import logger
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
from .dependencies.api import (
    verify_jwt, 
    get_payload_from_jwt, 
    get_filter_params, 
    validate_phone_number,
)
from contacts.db.crud.contacts import create_contact as create_contact_
from contacts.helpers.contacts import user_has_contact


router = APIRouter()


@router.post(
    "", 
    response_model=ContactInResponse, 
    status_code=201,
    dependencies=[Depends(verify_jwt), Depends(validate_phone_number)]
)
async def create_contact(
    request_contact: ContactInCreate,
    payload: dict = Depends(get_payload_from_jwt),
    db_session: AsyncSession = Depends(get_session),
) -> ContactInResponse:
    # TODO validate email (or already validated by pydantic?)
    request_user_id = int(payload["sub"])

    if await user_has_contact(
        user_id=request_user_id,
        phone_number=request_contact.phone_number,
        session=db_session,
    ):
        raise HTTPException(status_code=409, detail=f"phone number already exist")

    contact = await create_contact_(
        owner_id=request_user_id,
        db_session=db_session,
        **request_contact.dict(),
    )

    return ContactInResponse(
        contact=ContactWithId(**contact.dict())
    )


@router.get(
    "", 
    response_model=ContactsInResponse,
    dependencies=[Depends(verify_jwt)],
)
async def get_contacts(
    order_by: str = "last_name",
    filter_params: FilterParams = Depends(get_filter_params),
    payload: str = Depends(get_payload_from_jwt),
    db_session: AsyncSession = Depends(get_session),
) -> ContactsInResponse:
    user_id = int(payload["sub"])

    async with db_session.begin():
        # Get only user-owned contacts
        if payload["role"] == "user":
            filter_params.owner_id = user_id
            stmt = (
                select(Contact).
                filter_by(
                    **filter_params.dict(exclude_none=True),
                )
            )

        if payload["role"] == "admin":
            stmt = (
                select(Contact).
                filter_by(**filter_params.dict(exclude_none=True))
            )

        stmt = stmt.order_by(order_by)
        result: ChunkedIteratorResult = await db_session.execute(stmt)

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


@router.put(
    "", 
    response_model=ContactInResponse,
    dependencies=[Depends(verify_jwt), Depends(validate_phone_number)],
)
async def update_contact(
    request_contact: ContactInUpdate,
    contact_id: str,
    db_session: AsyncSession = Depends(get_session),
) -> ContactInResponse:
    ...
