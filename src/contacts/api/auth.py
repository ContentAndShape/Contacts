from fastapi import (
    APIRouter, 
    Request, 
    HTTPException, 
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from contacts.models.schemas.auth import Token, PayloadData
from contacts.models.schemas.users import BaseUser
from contacts.models.db.entities import UserInDb
from contacts.helpers.security import generate_jwt
from contacts.helpers.auth import authenticate_user
from .dependencies.db import get_session
from .dependencies.api import oauth2_scheme, get_payload_from_jwt
from contacts.db.crud.users import get_user


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
        raise HTTPException(status_code=401, detail="Incorrect username or password")

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


@router.get("/me", response_model=BaseUser)
async def get_me(
    request: Request,
    token: Token = Depends(oauth2_scheme),
    payload: PayloadData = Depends(get_payload_from_jwt),
    db_session: AsyncSession = Depends(get_session),
) -> BaseUser:
    user = await get_user(session=db_session, id=payload.sub)
    
    return BaseUser(id=user.id, role=user.role)
