import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from sqlalchemy.future import select

from contacts.models.db.tables import Contact
from contacts.models.db.entities import ContactInDb


async def create_contact(
    owner_id: int,
    last_name: str,
    first_name: str,
    middle_name: str,
    organisation: str,
    job_title: str,
    email: str,
    phone_number: str,
    db_session: AsyncSession,
) -> ContactInDb:
    contact_id = str(uuid.uuid4())

    async with db_session.begin():
        stmt = (
            insert(Contact).
            values(
                id=contact_id,
                owner_id=owner_id,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                organisation=organisation,
                job_title=job_title,
                email=email,
                phone_number=phone_number,
            )
        )
        await db_session.execute(stmt)
        stmt = (
            select(Contact).where(Contact.id == contact_id)
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
