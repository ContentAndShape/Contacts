import asyncio
from uuid import UUID

import pytest
import pytest_asyncio
from pytest import FixtureRequest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert
from sqlalchemy.future import select
from sqlalchemy.engine import ScalarResult
from alembic.config import Config
from alembic import command
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

from src.contacts.core.settings import get_settings
from src.contacts.main import get_app
from src.contacts.models.db.tables import Base
from src.contacts.helpers.security import hash_password
from src.contacts.models.db.tables import User, Contact
from . import model_generator

# APP
APP = get_app()
API_URL = f'http://127.0.0.1:8000/api/v1'
SETTINGS = get_settings()

# DB
NON_CACHED_DB_CONN_STR = SETTINGS.db_conn_str
NON_CACHED_ASYNC_DB_CONN_STR = SETTINGS.async_db_conn_str + "?prepared_statement_cache_size=0"

ALEMBIC_CFG = Config()
ALEMBIC_CFG.set_main_option("script_location", "src/contacts/db/migrations")
ALEMBIC_CFG.set_main_option('sqlalchemy.url', NON_CACHED_ASYNC_DB_CONN_STR)

ENGINE = create_engine(NON_CACHED_DB_CONN_STR)
ASYNC_ENGINE = create_async_engine(NON_CACHED_ASYNC_DB_CONN_STR)
ASYNC_SESSION = sessionmaker(
    ASYNC_ENGINE,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope='session')
def event_loop(request: FixtureRequest):
    """Create an instance of the default event loop for each test case.
    https://github.com/pytest-dev/pytest-asyncio/issues/38#issuecomment-264418154
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def create_tables(request: FixtureRequest) -> None:
    Base.metadata.create_all(ENGINE)

    def drop_tables() -> None:
        Base.metadata.drop_all(ENGINE)

    request.addfinalizer(drop_tables)


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(app=APP, base_url=API_URL) as client, LifespanManager(APP):
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
        user.__dict__["password"] = password
        
    return user


async def create_contact(
    owner_id: int,
    phone_number: str | None = None,
    id: UUID | None = None,
    last_name: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
    organisation: str | None = None,
    job_title: str | None = None,
    email: str | None = None,
) -> ScalarResult:
    default_contact = model_generator.Contact(owner_id=owner_id)
    id = id or default_contact.id
    phone_number = phone_number or default_contact.phone_number
    last_name = last_name or default_contact.last_name
    first_name = first_name or default_contact.first_name
    middle_name = middle_name or default_contact.middle_name
    organisation = organisation or default_contact.organisation
    job_title = job_title or default_contact.job_title
    email = email or default_contact.email

    id = str(id)

    async with ASYNC_SESSION() as session, session.begin():
        stmt = (
            insert(Contact).
            values(
                id=id,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                owner_id=owner_id,
                organisation=organisation,
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


async def get_access_token(username: str, password: str) -> str:
    async with AsyncClient(app=APP, base_url=API_URL) as client:
        data = {
            "username": username,
            "password": password,
        }
        res = await client.post(url="/auth/token", data=data)
    
    return res.json()["access_token"]


def get_headers(token: str) -> dict:
    return {
        "Authorization": "Bearer " + token,
    }
