from sqlalchemy.orm import (
    declarative_base, 
    declared_attr,
    relationship,
)
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID

from .metaclasses import RoleEnum


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"


Base = declarative_base(cls=Base)


class User(Base):
    id = Column(Integer, primary_key=True)
    contacts = relationship("Contact", back_populates="owner")
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)


class Contact(Base):
    id = Column(UUID, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="contacts")
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=False)
    organisation = Column(String(100))
    job_title = Column(String(100))
    email = Column(String(100), nullable=False)
    phone_number = Column(String(100), nullable=False)
