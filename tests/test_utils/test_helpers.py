import datetime
import jwt

import pytest

from src.contacts.models.schemas.auth import PayloadData
from src.contacts.helpers.auth import authenticate_user
from src.contacts.helpers.contacts import contact_is_owned_by_user, user_has_contact_with_such_number
from src.contacts.helpers.security import (
    validate_jwt,
    hash_password,
    passwords_match,
    get_payload_from_jwt,
)
from src.contacts.main import get_app
from src.contacts.helpers.security import ALGORITHM
from src.contacts.resources.errors.auth import MALFORMED_TOKEN_EXCEPTION
from ..conftest import ASYNC_SESSION, create_user, create_contact, create_tables, client
from ..model_generator import User, Contact


APP = get_app()


@pytest.mark.usefixtures("create_tables")
class TestAuth:
    @pytest.mark.asyncio
    async def test_success(self):
        user_pass = User().password
        user = await create_user(password=user_pass)
        user = await authenticate_user(
            username=user.username,
            password=user_pass,
            session=ASYNC_SESSION(),
        )
        assert user is not None

    @pytest.mark.asyncio
    async def test_failure(self):
        user_pass = User().password
        user = await create_user(password=user_pass)
        user = await authenticate_user(
            username=user.username,
            password='definitely_invalid',
            session=ASYNC_SESSION(),
        )
        assert user is None


@pytest.mark.usefixtures("create_tables")
class TestContacts:
    @pytest.mark.asyncio
    async def test_contact_owned_by_user(self):
        user = await create_user()
        contact = await create_contact(owner_id=user.id)
        assert await contact_is_owned_by_user(
            contact_id=contact.id,
            user_id=user.id,
            session=ASYNC_SESSION(),
        )

    @pytest.mark.asyncio
    async def test_contact_not_owned_by_user(self):
        user = await create_user()
        another_user = await create_user()
        contact = await create_contact(owner_id=another_user.id)
        assert not await contact_is_owned_by_user(
            contact_id=contact.id,
            user_id=user.id,
            session=ASYNC_SESSION(),
        )

    @pytest.mark.asyncio
    async def test_user_adds_duplicate_phone_num(self):
        phone_number = Contact(owner_id=-1).phone_number
        user = await create_user()
        await create_contact(owner_id=user.id, phone_number=phone_number)
        assert await user_has_contact_with_such_number(
            user_id=user.id,
            phone_number=phone_number,
            session=ASYNC_SESSION(),
        )

    @pytest.mark.asyncio
    async def test_user_adds_new_phone_num(self):
        user = await create_user()
        await create_contact(owner_id=user.id)
        new_phone_number = Contact(owner_id=-1).phone_number
        assert not await user_has_contact_with_such_number(
            user_id=user.id,
            phone_number=new_phone_number,
            session=ASYNC_SESSION(),
        )

