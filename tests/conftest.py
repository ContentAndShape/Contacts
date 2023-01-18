import os
import asyncio
from uuid import UUID

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
from src.contacts.models.db.tables import User, Contact
from . import model_generator


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
    username: str | None = None,
    id: int | None = None,
    password: str | None = None,
    role: str | None = None,
) -> ScalarResult:
    default_user = model_generator.User()
    id = id or default_user.id
    username = username or default_user.username
    password = password or default_user.password
    role = role or default_user.role

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


async def create_contact(
    owner_id: str,
    phone_number: str,
    id: UUID | None = None,
    last_name: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
    organistation: str | None = None,
    job_title: str | None = None,
    email: str | None = None,
) -> ScalarResult:
    default_contact = model_generator.Contact
    id = id or str(default_contact.id)
    last_name = last_name or default_contact.last_name
    first_name = first_name or default_contact.first_name
    middle_name = middle_name or default_contact.middle_name
    organistation = organistation or default_contact.organistation
    job_title = job_title or default_contact.job_title
    email = email or default_contact.email

    async with ASYNC_SESSION() as session, session.begin():
        stmt = (
            insert(Contact).
            values(
                id=id,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                owner_id=owner_id,
                organistation=organistation,
                job_title=job_title,
                email=email,
                phone_number=phone_number,
            )
        )
        await session.execute(stmt)
        stmt = (
            select(Contact).
            where(Contact.id == id)
        )
        contact = await session.scalar(stmt)

        return contact
