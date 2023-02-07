from fastapi import (
    APIRouter, 
    Request, 
    HTTPException, 
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from contacts.models.schemas.auth import Token, PayloadData
from contacts.models.db.entities import UserInDb
from contacts.helpers.security import generate_jwt
from contacts.helpers.auth import authenticate_user
from .dependencies.db import get_session
from contacts.resources.errors.auth import (
    INCORRECT_CREDENTIALS_EXCEPTION,
)


router = APIRouter()


@router.post("/token", response_model=Token)
async def access_token_login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_session),
) -> Token:
    user: UserInDb = await authenticate_user(
        form_data.username, 
        form_data.password, 
        db_session,
    )

    if user is None:
        raise INCORRECT_CREDENTIALS_EXCEPTION

    data = PayloadData(
        sub=user.id,
        role=user.role,
    )
    token = generate_jwt(
        payload=data,
        lifespan_min=30,
        secret=request.app.state.secret,
    )

    return Token(access_token=token, token_type="bearer")
