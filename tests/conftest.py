import os
import asyncio
from random import randint

import pytest
import pytest_asyncio
from pytest import FixtureRequest
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession,
)
from alembic.config import Config
from alembic import command
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert
from sqlalchemy.future import select
from sqlalchemy.engine import ScalarResult
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

from src.contacts.core.settings import get_settings
from src.contacts.main import app
from src.contacts.helpers.security import hash_password
from src.contacts.models.db.metaclasses import RoleEnum
from src.contacts.models.db.tables import User


SETTINGS = get_settings()
ALEMBIC_CFG = Config(f"{os.path.abspath('.')}/alembic.ini")
ASYNC_ENGINE = create_async_engine(SETTINGS.async_db_conn_str + "?prepared_statement_cache_size=0")
ASYNC_SESSION = sessionmaker(
    ASYNC_ENGINE,
    expire_on_commit=False,
    class_=AsyncSession,
)
API_URL = f'http://127.0.0.1:8000/api/v1'


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case.
    https://github.com/pytest-dev/pytest-asyncio/issues/38#issuecomment-264418154
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def create_tables(request: FixtureRequest) -> None:
    command.upgrade(ALEMBIC_CFG, "+1")

    def drop_tables() -> None:
        command.downgrade(ALEMBIC_CFG, "-1")

    request.addfinalizer(drop_tables)


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(app=app, base_url=API_URL) as client, LifespanManager(app):
        yield client


async def create_user(
    username: str,
    id: int = None,
    password: str = '123',
    role: RoleEnum = 'user',
) -> ScalarResult:

    if id is None:
        id = randint(0, 1000)

    async with ASYNC_SESSION() as session, session.begin():
        stmt = (
            insert(User).
            values(
                id=id,
                username=username,
                hashed_password=hash_password(password),
                role=role,
            )
        )
        await session.execute(stmt)
        stmt = (
            select(User).
            where(User.id == id)
        )
        user = await session.scalar(stmt)
        
    return user
