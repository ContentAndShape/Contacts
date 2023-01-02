from fastapi import Request
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


def get_session(request: Request) -> AsyncSession:
    Session = sessionmaker(
        request.app.state.engine,
        class_=AsyncSession,
    )
    return Session()