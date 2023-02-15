import pytest
from httpx import AsyncClient

from ..conftest import create_user, get_access_token, get_headers
from .. import model_generator
from src.contacts.resources.errors.auth import (
    INCORRECT_CREDENTIALS_EXCEPTION,
)
from src.contacts.resources.errors.users import (
    USER_ID_EXIST_EXCEPTION,
    USERNAME_EXIST_EXCEPTION,
)
from src.contacts.resources.errors.auth import MALFORMED_TOKEN_EXCEPTION


@pytest.mark.usefixtures("create_tables")
class TestAuth:
    @pytest.mark.asyncio
    async def test_incorrect_creds(self, client: AsyncClient):
        username = 'foo1'
        password = '123'
        user = await create_user(username=username, password=password)
        data = {
            'username': username,
            'password': 'invalid',
        }

        response = await client.post(url="/auth/token", data=data)

        assert response.status_code == 401
        assert response.json()["detail"] == INCORRECT_CREDENTIALS_EXCEPTION.detail

    @pytest.mark.asyncio
    async def test_success(self, client: AsyncClient):
        username = 'foo2'
        password = '123'
        user = await create_user(username=username, password=password)
        data = {
            'username': username,
            'password': password,
        }

        response = await client.post(url="/auth/token", data=data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_malformed_token(self, client: AsyncClient):
        user = await create_user()
        token = await get_access_token(username=user.username, password=user.password)
        header, payload, signature = token.split(".")
        sign_chars = [*signature]
        sign_chars[-1] = "o"
        malformed_token = f"{header}.{payload}.{''.join(sign_chars)}"
        
        response = await client.get("/users/me", headers=get_headers(malformed_token))
        assert response.status_code == 401
        assert response.json()["detail"] == MALFORMED_TOKEN_EXCEPTION.detail


@pytest.mark.usefixtures("create_tables")
class TestRegister:
    @pytest.mark.asyncio
    async def test_duplicate_id(self, client: AsyncClient):
        existing_user = await create_user()
        user = model_generator.User()
        user.id = existing_user.id
        json = {
            "id": user.id,
            "username": user.username,
            "password": user.password,
            "role": user.role,
        }

        response = await client.post(url="/users/register", json=json)
        assert response.status_code == 409
        assert response.json()["detail"] == USER_ID_EXIST_EXCEPTION.detail

    @pytest.mark.asyncio
    async def test_duplicate_username(self, client: AsyncClient):
        existing_user = await create_user()
        user = model_generator.User()
        user.username = existing_user.username
        json = {
            "id": user.id,
            "username": user.username,
            "password": user.password,
            "role": user.role,
        }

        response = await client.post(url="/users/register", json=json)
        assert response.status_code == 409
        assert response.json()["detail"] == USERNAME_EXIST_EXCEPTION.detail

    @pytest.mark.asyncio
    async def test_201(self, client: AsyncClient):
        user = model_generator.User()
        json = {
            "id": user.id,
            "username": user.username,
            "password": user.password,
            "role": user.role,
        }

        response = await client.post(url="/users/register", json=json)
        assert response.status_code == 201


@pytest.mark.usefixtures("create_tables")
class TestGet:
    @pytest.mark.asyncio
    async def test_get_me(self, client: AsyncClient):
        user = await create_user()
        token = await get_access_token(username=user.username, password=user.password)

        response = await client.get(url="/users/me", headers=get_headers(token))
        assert response.status_code == 200
