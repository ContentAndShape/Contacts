import pytest
from httpx import AsyncClient

from ..conftest import create_user


@pytest.mark.usefixtures("create_tables")
class TestLogin:

    @pytest.mark.asyncio
    async def test_login_401(self, client: AsyncClient):
        username = 'foo1'
        password = '123'
        user = await create_user(username=username, password=password)
        data = {
            'username': username,
            'password': 'invalid',
        }

        response = await client.post(url="/auth/token", data=data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_200(self, client: AsyncClient):
        username = 'foo2'
        password = '123'
        user = await create_user(username=username, password=password)
        data = {
            'username': username,
            'password': password,
        }

        response = await client.post(url="/auth/token", data=data)

        assert response.status_code == 200
        