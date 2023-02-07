from loguru import logger
from fastapi import (
    APIRouter, 
    Request, 
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from contacts.models.schemas.users import UserInCreate, UserInResponse, BaseUser
from contacts.models.schemas.auth import PayloadData
from contacts.models.db.entities import UserInDb
from contacts.api.dependencies.api import (
    process_jwt,
    check_user_uniqueness,
    get_payload_from_jwt, 
)
from contacts.api.dependencies.db import get_session
from contacts.db.crud.users import create_user, get_user
from contacts.helpers.security import hash_password


router = APIRouter()


@router.get(
    "/me",
    response_model=BaseUser,
    dependencies=[Depends(process_jwt)],
    )
async def get_me(
    request: Request,
    payload: PayloadData = Depends(get_payload_from_jwt),
    db_session: AsyncSession = Depends(get_session),
) -> BaseUser:
    # TODO return username instead of id
    user = await get_user(session=db_session, id=payload.sub)
    return BaseUser(id=user.id, role=user.role)


@router.post(
    "/register", 
    response_model=UserInResponse,
    status_code=201, 
    dependencies=[Depends(check_user_uniqueness)],
)
async def register_user(
    user: UserInCreate,
    db_session: AsyncSession = Depends(get_session),
) -> UserInResponse:
    # TODO exclude user id from body
    user = UserInDb(
        id=user.id,
        username=user.username,
        hashed_password=hash_password(user.password),
        role=user.role,
    )
    user = await create_user(session=db_session, user=user)
    return UserInResponse(
        user=BaseUser(id=user.id, role=user.role)
    )
