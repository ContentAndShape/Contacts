from dataclasses import asdict

import pytest
from httpx import AsyncClient

from ..conftest import create_user, create_contact, get_access_token, get_headers
from .. import model_generator
from src.contacts.models.schemas.meta import UserRoleEnum
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
        contact = model_generator.Contact(owner_id=user.id)
        contact.phone_number += "11111"
        contact.id = str(contact.id)

        # Invalid length
        response = await client.post(
            url="/contacts", json=asdict(contact), headers=get_headers(token)
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
            url="/contacts", json=asdict(contact), headers=get_headers(token)
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
        contact_in_db = await create_contact(owner_id=user.id)
        contact = model_generator.Contact(owner_id=user.id)
        contact.id = str(contact.id)
        contact.phone_number = contact_in_db.phone_number

        response = await client.post(
            url="/contacts", json=asdict(contact), headers=get_headers(token)
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
        contact = model_generator.Contact(owner_id=user.id)
        contact.id = str(contact.id)

        response = await client.post(
            url="/contacts", json=asdict(contact), headers=get_headers(token)
        )
        assert response.status_code == 201


@pytest.mark.usefixtures("create_tables")
class TestRead:
    @pytest.mark.asyncio
    async def test_400_wrong_order_param(self, client: AsyncClient):
        user = model_generator.User()
        user_data = {
            "username": user.username,
            "password": user.password,
        }
        user = await create_user(**user_data)
        token = await get_access_token(**user_data)
        contact = await create_contact(owner_id=user.id)
        params = {
            "order_by": "foo",
        }

        response = await client.get(url="/contacts", headers=get_headers(token), params=params)
        assert response.status_code == 400
        assert "Incorrect order parameter" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_admin_get_all_contacts(self, client: AsyncClient):
        users_id = []
        contacts_id = []
        
        for i in range(5):
            user = await create_user()
            users_id.append(user.id)

        for id in users_id:
            contact = await create_contact(owner_id=id)
            contacts_id.append(contact.id)

        admin = await create_user(role=UserRoleEnum.admin.value)
        token = await get_access_token(username=admin.username, password=admin.password)

        response = await client.get(url="/contacts", headers=get_headers(token))
        response_contacts_id = [
            contact["id"] for contact in response.json()["contacts"]
        ]
        for id in contacts_id:
            assert id in response_contacts_id


    @pytest.mark.asyncio
    async def test_user_get_all_contacts(self, client: AsyncClient):
        for i in range(5):
            user = await create_user()
            await create_contact(owner_id=user.id)

        user = await create_user()
        contact = await create_contact(owner_id=user.id)
        token = await get_access_token(username=user.username, password=user.password)

        response = await client.get(url="/contacts", headers=get_headers(token))
        assert response.json()["contacts"][0]["id"] == contact.id


@pytest.mark.usefixtures("create_tables")
class TestUpdate:
    @pytest.mark.asyncio
    async def test_admin_update_user_contact(self, client: AsyncClient):
        admin = await create_user(role=UserRoleEnum.admin.value)
        user = await create_user()
        contact = model_generator.Contact(owner_id=user.id)
        await create_contact(id=contact.id, owner_id=user.id)
        token = await get_access_token(username=admin.username, password=admin.password)
        contact.id = str(contact.id)

        response = await client.put(url=f"/contacts/{contact.id}", headers=get_headers(token), json=asdict(contact))
        assert response.status_code == 204


#TODO test update user/admin role
#TODO test delete user/admin role
