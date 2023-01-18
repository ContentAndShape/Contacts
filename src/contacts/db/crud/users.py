from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from contacts.models.db.tables import User
from contacts.models.db.entities import UserInDb


async def get_user(username: str, session: AsyncSession) -> UserInDb | None:
    async with session.begin():
        stmt = select(User).where(User.username == username)
        user: User = await session.scalar(stmt)

        if user is None:
            return None

        return UserInDb(
            id=user.id,
            username=user.username,
            hashed_password=user.hashed_password,
            role=user.role.value,
        )
