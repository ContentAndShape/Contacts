from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from contacts.models.schemas.contacts import (
    BaseContact,
    ContactWithId,
    ContactInCreate,
    ContactInUpdate,
    ContactInDelete,
    ContactInResponse,
    ContactsInResponse
)
from contacts.models.schemas.auth import Token, PayloadData
from contacts.models.schemas.meta import ContactsFilterParams, OrderContactsByEnum
from .dependencies.db import get_session
from .dependencies.api import (
    process_jwt, 
    get_payload_from_jwt, 
    get_filter_params, 
    validate_phone_number,
)
from contacts.db.crud.contacts import get_user_contacts_with_filters, create_contact as create_contact_
from contacts.helpers.contacts import user_has_contact


router = APIRouter()


@router.post(
    "", 
    response_model=ContactInResponse, 
    status_code=201,
    dependencies=[Depends(process_jwt), Depends(validate_phone_number)],
)
async def create_contact(
    request_contact: ContactInCreate,
    request: Request,
    payload: PayloadData = Depends(get_payload_from_jwt),
    db_session: AsyncSession = Depends(get_session),
) -> ContactInResponse:
    # TODO validate email (or already validated by pydantic?)
    request_user_id = payload.sub

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
    dependencies=[Depends(process_jwt)],
)
async def get_contacts(
    request: Request,
    order_by: str = OrderContactsByEnum.last_name,
    filter_params: ContactsFilterParams = Depends(get_filter_params),
    payload: PayloadData = Depends(get_payload_from_jwt),
    db_session: AsyncSession = Depends(get_session),
) -> ContactsInResponse:
    logger.debug(f"Filter param: {filter_params}")
    if order_by not in OrderContactsByEnum._member_names_:
        raise HTTPException(status_code=400, detail="Incorrect order parameter")

    contacts = await get_user_contacts_with_filters(
        user_id=payload.sub,
        filter_params=filter_params,
        order_by=order_by,
        db_session=db_session,
    )
    return ContactsInResponse(
        contacts=[ContactWithId(**contact.dict()) for contact in contacts]
    )


@router.put(
    "", 
    response_model=ContactInResponse,
    dependencies=[Depends(validate_phone_number)],
)
async def update_contact(
    request_contact: ContactInUpdate,
    contact_id: str,
    db_session: AsyncSession = Depends(get_session),
) -> ContactInResponse:
    ...
