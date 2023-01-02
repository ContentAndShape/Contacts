from fastapi import APIRouter, Response, Request, HTTPException, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from contacts.models.schemas.users import (
    UserInLogin,
    UserInCreate,
    UserInResponse,
    BaseUser,
)
from contacts.helpers.security import get_jwt, passwords_match
from contacts.models.db.tables import User
from .dependencies.db import get_session


router = APIRouter()


@router.post("/login", response_model=UserInResponse)
async def login(
    request_user: UserInLogin,
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> UserInResponse:

    async with session.begin():
        stmt = select(User).where(User.username == request_user.username)
        db_user = await session.scalar(stmt)

        if db_user is None:
            raise HTTPException(status_code=404)

        if not passwords_match(
            plain_pw=request_user.password, hashed_pw=db_user.hashed_password
        ):
            raise HTTPException(status_code=401)

        payload = BaseUser(
            id=db_user.id,
            role=db_user.role.value,
        )

    token = get_jwt(
        payload=payload.dict(),
        subject="access",
        lifespan_min=30,
        secret=request.app.state.secret,
    )

    # May be swapped to return token along with response
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
    )

    return UserInResponse(user=payload)


# @router.post("/register", response_model=UserInResponse)
# async def register(user: UserInCreate, db_interface: ...):
#     ...
