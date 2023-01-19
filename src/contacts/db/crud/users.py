from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from contacts.models.db.tables import User
from contacts.models.db.entities import UserInDb


async def get_user(
    session: AsyncSession,
    id: int | None = None,
    username: str | None = None,
) -> UserInDb | None:

    async with session.begin():
        if id:
            stmt = select(User).where(User.id == id)
        elif username:
            stmt = select(User).where(User.username == username)
        else:
            return None

        user: User = await session.scalar(stmt)

        if user is None:
            return user

        return UserInDb(
            id=user.id,
            username=user.username,
            hashed_password=user.hashed_password,
            role=user.role.value,
        )
