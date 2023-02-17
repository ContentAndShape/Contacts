from dataclasses import asdict

import pytest

from src.contacts.db.crud.users import get_user, create_user
from src.contacts.helpers.security import hash_password, passwords_match
from src.contacts.models.db.entities import UserInDb
from ..conftest import create_tables, ASYNC_SESSION, create_user as fixture_create_user
from ..model_generator import User


@pytest.mark.usefixtures("create_tables")
class TestCreate:
    @pytest.mark.asyncio
    async def test_create_user(self):
        init_user = UserInDb(
            hashed_password=hash_password('123'),
            **asdict(User()),
        )
        created_user = await create_user(session=ASYNC_SESSION(), user=init_user)

        assert created_user == init_user


@pytest.mark.usefixtures("create_tables")
class TestGet:
    @pytest.mark.asyncio
    async def test_get_user_by_existing_id(self):
        user_model = User()
        await fixture_create_user(**asdict(user_model))
        init_user = UserInDb(
            hashed_password=hash_password(user_model.password),
            **asdict(user_model),
        )
        got_user = await get_user(session=ASYNC_SESSION(), id=init_user.id)
        
        for field, val in got_user.dict().items():
            if field == "hashed_password":
                continue

            assert val == init_user.dict()[field]

        assert passwords_match(user_model.password, got_user.hashed_password)

    @pytest.mark.asyncio
    async def test_get_user_by_non_existing_id(self):
        await fixture_create_user(**asdict(User()))
        got_user = await get_user(session=ASYNC_SESSION(), id=00000)

        assert got_user is None

    @pytest.mark.asyncio
    async def test_get_user_by_existing_username(self):
        user_model = User()
        await fixture_create_user(**asdict(user_model))
        init_user = UserInDb(
            hashed_password=hash_password(user_model.password),
            **asdict(user_model),
        )
        got_user = await get_user(session=ASYNC_SESSION(), username=init_user.username)
        
        for field, val in got_user.dict().items():
            if field == "hashed_password":
                continue

            assert val == init_user.dict()[field]

        assert passwords_match(user_model.password, got_user.hashed_password)

    @pytest.mark.asyncio
    async def test_get_user_by_non_existing_username(self):
        await fixture_create_user(**asdict(User()))
        got_user = await get_user(session=ASYNC_SESSION(), username='404')

        assert got_user is None
