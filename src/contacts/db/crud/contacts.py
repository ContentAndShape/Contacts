import uuid
from typing import List

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy import insert, update, delete
from sqlalchemy.future import select

from contacts.models.db.tables import Contact
from contacts.models.db.entities import ContactInDb
from contacts.models.schemas.meta import ContactsFilterParams, UserRoleEnum
from .users import get_user


async def create_contact(
    contact: ContactInDb,
    db_session: AsyncSession,
) -> ContactInDb:

    async with db_session.begin():
        stmt = (
            insert(Contact).values(**contact.dict())
        )
        await db_session.execute(stmt)
        stmt = (
            select(Contact).where(Contact.id == contact.id)
        )
        contact: Contact = await db_session.scalar(stmt)

        return ContactInDb(
            id=contact.id,
            owner_id=contact.owner_id,
            last_name=contact.last_name,
            first_name=contact.first_name,
            middle_name=contact.middle_name,
            organisation=contact.organisation,
            job_title=contact.job_title,
            email=contact.email,
            phone_number=contact.phone_number,
        )


async def get_contact(id: uuid.UUID, db_session: AsyncSession) -> ContactInDb | None:
    async with db_session.begin():
        stmt = (
            select(Contact).
            where(Contact.id == str(id))
        )
        contact = await db_session.scalar(stmt)
        if contact is None:
            return contact

        return ContactInDb(
            id=contact.id,
            owner_id=contact.owner_id,
            last_name=contact.last_name,
            first_name=contact.first_name,
            middle_name=contact.middle_name,
            organisation=contact.organisation,
            job_title=contact.job_title,
            email=contact.email,
            phone_number=contact.phone_number,
        )


async def get_user_contacts_with_filters(
    user_id: int,
    filter_params: ContactsFilterParams,
    order_by: str,
    db_session: AsyncSession,
) -> List[ContactInDb]:
    user_in_db = await get_user(id=user_id, session=db_session)

    async with db_session.begin():
        if user_in_db.role == UserRoleEnum.user.value:
            filter_params.owner_id = user_id
            stmt = (
                select(Contact).
                filter_by(**filter_params.dict(exclude_none=True))
            )

        if user_in_db.role == UserRoleEnum.admin.value:
            stmt = (
                select(Contact).
                filter_by(**filter_params.dict(exclude_none=True))
            )

        stmt = stmt.order_by(order_by)
        result: ChunkedIteratorResult = await db_session.execute(stmt)

        return [ContactInDb(
            id=contact.id,
            owner_id=contact.owner_id,
            last_name=contact.last_name,
            first_name=contact.first_name,
            middle_name=contact.middle_name,
            organisation=contact.organisation,
            job_title=contact.job_title,
            email=contact.email,
            phone_number=contact.phone_number,
        ) for contact in result.scalars().all()]


async def update_contact(
    db_session: AsyncSession,
    id: uuid.UUID,
    last_name: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
    organisation: str | None = None,
    job_title: str | None = None,
    email: str | None = None,
    phone_number: str | None = None,
) -> None:
    async with db_session.begin():
        old_contact = await db_session.scalar(select(Contact).where(Contact.id == str(id)))
        stmt = (
            update(Contact).
            where(Contact.id == str(id)).
            values(
                last_name = last_name or old_contact.last_name,
                first_name=first_name or old_contact.first_name,
                middle_name=middle_name or old_contact.middle_name,
                organisation=organisation or old_contact.organisation,
                job_title=job_title or old_contact.job_title,
                email=email or old_contact.email,
                phone_number=phone_number or old_contact.phone_number,
            ).returning(
                Contact.id,
                Contact.owner_id,
                Contact.last_name,
                Contact.first_name,
                Contact.middle_name,
                Contact.organisation,
                Contact.job_title,
                Contact.email,
                Contact.phone_number,
            )
        )
        await db_session.execute(stmt)


async def delete_contact(db_session: AsyncSession, id: uuid.UUID) -> None:
    async with db_session.begin():
        stmt = delete(Contact).where(Contact.id == str(id))
        await db_session.execute(stmt)
