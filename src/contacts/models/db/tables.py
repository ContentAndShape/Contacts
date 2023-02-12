from typing import Set
from uuid import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase, 
    relationship,
    declared_attr,
)
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Enum,
)

from .metaclasses import RoleEnum


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"


# Base = declarative_base(cls=Base)


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    contacts: Mapped[Set["Contact"]] = relationship(back_populates="owner")
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)


class Contact(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="contacts")
    last_name = Column(String(100))
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    organisation = Column(String(100))
    job_title = Column(String(100))
    email = Column(String(100))
    phone_number = Column(String(100), nullable=False)
