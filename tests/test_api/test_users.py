from random import randint

import pytest
from httpx import AsyncClient

from ..conftest import create_user


@pytest.mark.usefixtures("create_tables")
class TestLogin:

    @pytest.mark.asyncio
    async def test_login_404(self, client: AsyncClient):
        user = await create_user('foo')
        json = {
            'username': 'bar',
            "password": '123',
        }

        response = await client.post(url="/auth/login", json=json)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_login_401(self, client: AsyncClient):
        user = await create_user('foo1')
        json = {
            'username': 'foo1',
            'password': 'invalid',
        }

        response = await client.post(url="/auth/login", json=json)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_200(self, client: AsyncClient):
        user = await create_user('foo2')
        json = {
            'username': 'foo2',
            'password': '123',
        }

        response = await client.post(url="/auth/login", json=json)

        assert response.status_code == 200
        