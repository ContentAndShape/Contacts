from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from contacts.models.db.tables import Contact


def phone_number_is_valid(phone_number: str) -> bool:
    if len(phone_number) != 11:
        return False
    
    for char in phone_number:
        try:
            int(char)
        except ValueError:
            return False

    return True


async def user_has_contact(
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
