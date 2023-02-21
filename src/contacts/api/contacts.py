import uuid

from loguru import logger
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from contacts.models.db.entities import ContactInDb
from contacts.models.schemas.contacts import (
    ContactWithId,
    ContactInCreate,
    ContactInUpdate,
    ContactInResponse,
    ContactsInResponse
)
from contacts.models.schemas.auth import PayloadData
from contacts.models.schemas.meta import ContactsFilterParams, OrderContactsByEnum
from .dependencies.db import get_session
from .dependencies.api import (
    process_jwt, 
    get_payload_from_jwt, 
    validate_contact_ownership,
    check_contact_existence,
    get_filter_params, 
    validate_phone_number,
)
from contacts.db.crud.contacts import (
    get_user_contacts_with_filters, 
    create_contact as create_contact_, 
    update_contact as update_contact_,
    delete_contact as delete_contact_,
)
from contacts.helpers.contacts import user_has_contact_with_such_number
from contacts.resources.errors.contacts import (
    USER_HAS_PHONE_NUM_EXCEPTION,
    ORDER_PARAMS_EXCEPTION,
    CONTACT_DOES_NOT_EXIST_EXCEPTION,
)


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
    request_user_id = payload.sub

    if await user_has_contact_with_such_number(
        user_id=request_user_id,
        phone_number=request_contact.phone_number,
        session=db_session,
    ):
        raise USER_HAS_PHONE_NUM_EXCEPTION

    contact = await create_contact_(
        contact=ContactInDb(owner_id=request_user_id, **request_contact.dict()),
        db_session=db_session,
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
    if order_by not in OrderContactsByEnum._member_names_:
        raise ORDER_PARAMS_EXCEPTION

    contacts = await get_user_contacts_with_filters(
        user_id=payload.sub,
        filter_params=filter_params,
        order_by=order_by,
        db_session=db_session,
    )
    if len(contacts) == 0:
        raise CONTACT_DOES_NOT_EXIST_EXCEPTION

    return ContactsInResponse(
        contacts=[ContactWithId(**contact.dict()) for contact in contacts]
    )


@router.put(
    "/{contact_id}", 
    status_code=204,
    dependencies=[
    Depends(process_jwt),
    Depends(check_contact_existence),
    Depends(validate_contact_ownership),
    Depends(validate_phone_number),
    ],
)
async def update_contact(
    contact_id: uuid.UUID,
    request_contact: ContactInUpdate,
    payload: PayloadData = Depends(get_payload_from_jwt),
    db_session: AsyncSession = Depends(get_session),
) -> None:
    await update_contact_(db_session=db_session, id=contact_id, **request_contact.dict())


@router.delete(
    "/{contact_id}",
    status_code=204,
    dependencies=[
        Depends(process_jwt),
        Depends(check_contact_existence),
        Depends(validate_contact_ownership),
    ],
)
async def delete_contact(
    contact_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_session),
) -> None:
    await delete_contact_(db_session=db_session, id=contact_id)
