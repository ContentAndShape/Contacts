from fastapi import (
    APIRouter, 
    Request, 
    HTTPException, 
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from contacts.models.schemas.auth import Token
from contacts.helpers.security import generate_jwt
from contacts.helpers.auth import authenticate_user
from .dependencies.db import get_session


router = APIRouter()


@router.post("/token", response_model=Token)
async def access_token_login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_session),
) -> Token:
    logger.debug(f"Trying to auth user '{form_data.username}'")
    user = await authenticate_user(
        form_data.username, 
        form_data.password, 
        db_session,
    )

    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    data = {"sub": user.id}

    token = generate_jwt(
        payload=data,
        subject="access",
        lifespan_min=30,
        secret=request.app.state.secret,
    )

    return Token(access_token=token, token_type="bearer")
