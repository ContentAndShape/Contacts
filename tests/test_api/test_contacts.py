from dataclasses import asdict

import pytest
from httpx import AsyncClient

from ..conftest import create_user, create_contact, get_access_token, get_headers
from .. import model_generator
from src.contacts.models.schemas.meta import UserRoleEnum
from src.contacts.resources.errors.contacts import (
    PHONE_NUM_LEN_EXCEPTION,
    PHONE_NUM_FORMAT_EXCEPTION,
    USER_HAS_PHONE_NUM_EXCEPTION,
    ORDER_PARAMS_EXCEPTION,
    CONTACT_DOES_NOT_EXIST_EXCEPTION,
)
from src.contacts.resources.errors.users import (
    USER_CONTACT_OWNERSHIP_EXCEPTION,
)


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
        assert response.json()["detail"] == PHONE_NUM_LEN_EXCEPTION.detail

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
        assert response.json()["detail"] == PHONE_NUM_FORMAT_EXCEPTION.detail

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
        assert response.json()["detail"] == USER_HAS_PHONE_NUM_EXCEPTION.detail

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
        await create_contact(owner_id=user.id)
        params = {
            "order_by": "foo",
        }

        response = await client.get(url="/contacts", headers=get_headers(token), params=params)
        assert response.status_code == 400
        assert response.json()["detail"] == ORDER_PARAMS_EXCEPTION.detail

    @pytest.mark.asyncio
    async def test_404(self, client: AsyncClient):
        user = model_generator.User()
        user_data = {
            "username": user.username,
            "password": user.password,
        }
        user = await create_user(**user_data)
        token = await get_access_token(**user_data)

        response = await client.get(url="/contacts", headers=get_headers(token))
        assert response.status_code == 404
        assert response.json()["detail"] == CONTACT_DOES_NOT_EXIST_EXCEPTION.detail

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

    @pytest.mark.asyncio
    async def test_user_update_someones_contact(self, client: AsyncClient):
        user1 = await create_user()
        contact_update = model_generator.Contact(owner_id=user1.id)
        contact_update.id = str(contact_update.id)
        token = await get_access_token(user1.username, user1.password)
        user2 = await create_user()
        user2_contact = await create_contact(owner_id=user2.id)

        response = await client.put(url=f"/contacts/{user2_contact.id}", headers=get_headers(token), json=asdict(contact_update))
        assert response.status_code == 403
        assert response.json()["detail"] == USER_CONTACT_OWNERSHIP_EXCEPTION.detail

    @pytest.mark.asyncio
    async def test_user_update_own_contact(self, client: AsyncClient):
        user = await create_user()
        token = await get_access_token(user.username, user.password)
        contact = await create_contact(owner_id=user.id)
        contact_update = model_generator.Contact(owner_id=user.id)
        contact_update.id = str(contact_update.id)

        response = await client.put(url=f"/contacts/{contact.id}", headers=get_headers(token), json=asdict(contact_update))
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_404(self, client: AsyncClient):
        user = await create_user()
        token = await get_access_token(user.username, user.password)
        non_existing_contact = model_generator.Contact(owner_id=user.id)
        non_existing_contact.id = str(non_existing_contact.id)

        response = await client.put(url=f"/contacts/{non_existing_contact.id}", headers=get_headers(token), json=asdict(non_existing_contact))
        assert response.status_code == 404
        assert response.json()["detail"] == CONTACT_DOES_NOT_EXIST_EXCEPTION.detail


@pytest.mark.usefixtures("create_tables")
class TestDelete:
    @pytest.mark.asyncio
    async def test_admin_delete_user_contact(self, client: AsyncClient):
        admin = await create_user(role=UserRoleEnum.admin.value)
        user = await create_user()
        contact = model_generator.Contact(owner_id=user.id)
        await create_contact(id=contact.id, owner_id=user.id)
        token = await get_access_token(username=admin.username, password=admin.password)
        contact.id = str(contact.id)

        response = await client.delete(url=f"/contacts/{contact.id}", headers=get_headers(token))
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_user_delete_someones_contact(self, client: AsyncClient):
        user1 = await create_user()
        contact_update = model_generator.Contact(owner_id=user1.id)
        contact_update.id = str(contact_update.id)
        token = await get_access_token(user1.username, user1.password)
        user2 = await create_user()
        user2_contact = await create_contact(owner_id=user2.id)

        response = await client.delete(url=f"/contacts/{user2_contact.id}", headers=get_headers(token))
        assert response.status_code == 403
        assert response.json()["detail"] == USER_CONTACT_OWNERSHIP_EXCEPTION.detail

    @pytest.mark.asyncio
    async def test_user_delete_own_contact(self, client: AsyncClient):
        user = await create_user()
        token = await get_access_token(user.username, user.password)
        contact = await create_contact(owner_id=user.id)
        contact_update = model_generator.Contact(owner_id=user.id)
        contact_update.id = str(contact_update.id)

        response = await client.delete(url=f"/contacts/{contact.id}", headers=get_headers(token))
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_404(self, client: AsyncClient):
        user = await create_user()
        token = await get_access_token(user.username, user.password)
        non_existing_contact = model_generator.Contact(owner_id=user.id)
        non_existing_contact.id = str(non_existing_contact.id)

        response = await client.delete(url=f"/contacts/{non_existing_contact.id}", headers=get_headers(token))
        assert response.status_code == 404
        assert response.json()["detail"] == CONTACT_DOES_NOT_EXIST_EXCEPTION.detail
