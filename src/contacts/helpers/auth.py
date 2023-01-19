from sqlalchemy.ext.asyncio import AsyncSession

from contacts.models.db.entities import UserInDb
from contacts.db.crud.users import get_user
from .security import passwords_match


async def authenticate_user(
    username: str,
    password: str, 
    session: AsyncSession,
) -> UserInDb | None:
    user = await get_user(username=username, session=session)

    if user is None:
        return None

    if not passwords_match(plain_pw=password, hashed_pw=user.hashed_password):
        return None

    return user
