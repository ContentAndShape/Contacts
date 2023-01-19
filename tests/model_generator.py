from dataclasses import dataclass, field
import enum
import uuid
import string
import random


class Role(enum.Enum):
    admin = 'admin'
    user = 'user'


def rand_str(len: int = 10) -> str:
    return "".join([random.choice(string.ascii_letters) for i in range(len)])


def rand_email() -> str:
    return f"{rand_str()}@gmail.com"


def rand_phone_number(len: int = 11) -> str:
    return "".join([random.choice(string.digits) for i in range(len)])


@dataclass
class User:
    id: int = field(default_factory=lambda: random.randrange(0, 10000))
    username: str = field(default_factory=rand_str)
    password: str = field(default_factory=rand_str)
    role: Role = Role.user.value


@dataclass
class Contact:
    owner_id: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    phone_number: str = field(default_factory=rand_phone_number)
    last_name: str = field(default_factory=rand_str)
    first_name: str = field(default_factory=rand_str)
    middle_name: str = field(default_factory=rand_str)
    organisation: str = field(default_factory=rand_str)
    job_title: str = field(default_factory=rand_str)
    email: str = field(default_factory=rand_email)
