from dataclasses import asdict

import pytest
from httpx import AsyncClient

from ..conftest import create_user, create_contact, get_access_token
from .. import model_generator
#TODO make scheme for headers
#TODO assert response details with error strings from separate module

@pytest.mark.usefixtures("create_tables")
class TestCreate:
    @pytest.mark.asyncio
    async def test_422(self, client: AsyncClient):
        user = model_generator.User()
        user_data = {
            "username": user.username,
            "password": user.password,
        }
        user = await create_user(**user_data)
        token = await get_access_token(**user_data)
        headers = {
            "Authorization": "Bearer " + token,
        }
        contact = model_generator.Contact(owner_id=user.id)
        contact.phone_number += "11111"
        contact.id = str(contact.id)

        # Invalid length
        response = await client.post(
            url="/contacts", json=asdict(contact), headers=headers
        )
        assert response.status_code == 422
        assert "length" in response.json()["detail"]

        contact = model_generator.Contact(owner_id=user.id)
        contact.id = str(contact.id)
        phone_number_list = [*contact.phone_number]
        phone_number_list[-1] = "t"
        contact.phone_number = "".join(phone_number_list)

        # Invalid format
        response = await client.post(
            url="/contacts", json=asdict(contact), headers=headers
        )
        assert response.status_code == 422
        assert "format" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_409(self, client: AsyncClient):
        user = model_generator.User()
        user_data = {
            "username": user.username,
            "password": user.password,
        }
        user = await create_user(**user_data)
        token = await get_access_token(**user_data)
        headers = {
            "Authorization": "Bearer " + token,
        }
        contact_in_db = await create_contact(owner_id=user.id)
        contact = model_generator.Contact(owner_id=user.id)
        contact.id = str(contact.id)
        contact.phone_number = contact_in_db.phone_number

        response = await client.post(
            url="/contacts", json=asdict(contact), headers=headers
        )
        assert response.status_code == 409
        assert "already exist" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_201(self, client: AsyncClient):
        user = model_generator.User()
        user_data = {
            "username": user.username,
            "password": user.password,
        }
        user = await create_user(**user_data)
        token = await get_access_token(**user_data)
        headers = {
            "Authorization": "Bearer " + token,
        }
        contact = model_generator.Contact(owner_id=user.id)
        contact.id = str(contact.id)

        response = await client.post(
            url="/contacts", json=asdict(contact), headers=headers
        )
        assert response.status_code == 201


@pytest.mark.usefixtures("create_tables")
class TestRead:
    @pytest.mark.asyncio
    async def test_400_wrong_filters(self, client: AsyncClient):
        user = model_generator.User()
        user_data = {
            "username": user.username,
            "password": user.password,
        }
        user = await create_user(**user_data)
        token = await get_access_token(**user_data)
        headers = {
            "Authorization": "Bearer " + token,
        }
        contact = await create_contact(owner_id=user.id)
        params = {
            "foo": "bar",
            "order_by": "foo",
        }

        response = await client.get(url="/contacts", headers=headers, params=params)
        assert response.status_code == 400
        assert "Incorrect order parameter" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_200(self, client: AsyncClient):
        ...
