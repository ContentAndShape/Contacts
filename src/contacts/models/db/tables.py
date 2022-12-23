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
    create_engine
)
from sqlalchemy.dialects.postgresql import UUID, ENUM

from metaclasses import RoleEnum


engine = create_engine("postgresql://docker:docker@127.0.0.1:5432/docker")


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"


Base = declarative_base(cls=Base)


class User(Base):
    id = Column(Integer, primary_key=True)
    contacts = relationship("Contact", back_populates="owner")
    username = Column(String(100))
    hashed_password = Column(String(100))
    role = Column(ENUM(RoleEnum))


class Contact(Base):
    id = Column(UUID, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    last_name = Column(String(100))
    first_name = Column(String(100))
    middle_name = Column(String(100))
    organistation = Column(String(100))
    job_title = Column(String(100))
    email = Column(String(100))
    phone_number = Column(String(100))

Base.metadata.create_all(engine)