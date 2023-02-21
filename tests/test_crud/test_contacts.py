import uuid
from dataclasses import asdict

import pytest

from src.contacts.models.db.entities import ContactInDb
from src.contacts.models.schemas.meta import ContactsFilterParams
from ..model_generator import Contact, User
from ..conftest import create_user as create_user_, create_contact as create_contact_, get_contact as get_contact_,ASYNC_SESSION
from src.contacts.db.crud.contacts import create_contact, get_contact, get_user_contacts_with_filters, update_contact


@pytest.mark.usefixtures("create_tables")
class TestCreate:
    @pytest.mark.asyncio
    async def test_create_contact(self):
        user = await create_user_()
        contact = Contact(owner_id=user.id)
        contact = ContactInDb(**asdict(contact))
        created_contact = await create_contact(db_session=ASYNC_SESSION(), contact=contact)
        
        assert created_contact == contact


@pytest.mark.usefixtures("create_tables")
class TestRead:
    @pytest.mark.asyncio
    async def test_get_non_existing_contact(self):
        got_contact = await get_contact(id=uuid.uuid4(), db_session=ASYNC_SESSION())

        assert got_contact is None

    @pytest.mark.asyncio
    async def test_get_existing_contact(self):
        user = User()
        await create_user_(**asdict(user))
        contact_model = Contact(owner_id=user.id)
        created_contact = ContactInDb(**asdict(contact_model))
        await create_contact_(**created_contact.dict())
        got_contact = await get_contact(id=created_contact.id, db_session=ASYNC_SESSION())

        assert got_contact == created_contact

    @pytest.mark.asyncio
    async def test_get_user_contacts_with_filters(self):
        user = await create_user_(**asdict(User()))
        for i in range(3):
            contact_model = Contact(owner_id=user.id)
            await create_contact_(**asdict(contact_model))
        last_created_contact = ContactInDb(**asdict(contact_model))
        filters = ContactsFilterParams(last_name=contact_model.last_name)
        got_contacts = await get_user_contacts_with_filters(
            user_id=user.id,
            db_session=ASYNC_SESSION(),
            filter_params=filters,
            order_by='last_name',
        )
        
        assert got_contacts[0] == last_created_contact

    @pytest.mark.asyncio
    async def test_get_all_user_contacts(self):
        user = await create_user_(**asdict(User()))
        for i in range(3):
            await create_contact_(**asdict(Contact(owner_id=user.id)))
            filters = ContactsFilterParams()
            got_contacts = await get_user_contacts_with_filters(
                user_id=user.id,
                db_session=ASYNC_SESSION(),
                filter_params=filters,
                order_by='last_name',
            )

        assert len(got_contacts) == 3


@pytest.mark.usefixtures("create_tables")
class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_contact(self):
        user = await create_user_(**asdict(User()))
        contact = await create_contact_(owner_id=user.id)
        await update_contact(
            db_session=ASYNC_SESSION(),
            id=contact.id,
            last_name='updated',
            first_name='updated',
            middle_name='updated',
            organisation='updated',
            job_title='updated',
        )
        desired = ContactInDb(
            id=contact.id,
            owner_id=user.id,
            last_name='updated',
            first_name='updated',
            middle_name='updated',
            organisation='updated',
            job_title='updated',
            email=contact.email,
            phone_number=contact.phone_number,
        )
        updated = await get_contact_(id=contact.id)
        updated = ContactInDb(
            id=updated.id,
            owner_id=updated.owner_id,
            last_name=updated.last_name,
            first_name=updated.first_name,
            middle_name=updated.middle_name,
            organisation=updated.organisation,
            job_title=updated.job_title,
            email=updated.email,
            phone_number=updated.phone_number,
        )

        assert updated == desired

