import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from contacts.models.db.tables import Contact


def email_is_valid(email: str) -> bool:
    return False


async def contact_is_owned_by_user(
    contact_id: uuid.UUID, 
    user_id: int, 
    session: AsyncSession
) -> bool:
    async with session.begin():
        stmt = (
            select(Contact).
            where(Contact.id == str(contact_id))
        )
        contact: Contact = await session.scalar(stmt)

        return contact.owner_id == user_id


async def user_has_contact_with_such_number(
    user_id: int, phone_number: str, session: AsyncSession
) -> bool:
    async with session.begin():
        stmt = select(Contact).where(
            and_(
                Contact.phone_number == phone_number,
                Contact.owner_id == user_id,
            )
        )
        contact = await session.scalar(stmt)

        return True if contact else False
