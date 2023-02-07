from datetime import datetime, timedelta
import jwt
import bcrypt

from contacts.models.schemas.auth import PayloadData
from contacts.resources.errors.auth import (
    TOKEN_DECODE_EXCEPTION,
    EXPIRED_TOKEN_SIGNATURE_EXCEPTION,
    MALFORMED_TOKEN_EXCEPTION,
)


JWT_EXP_DELTA_MIN = 60 * 24
ALGORITHM = "HS256"


def generate_jwt(
    payload: PayloadData,
    lifespan_min: int,
    secret: str,
) -> str:
    payload.exp = datetime.utcnow() + timedelta(minutes=lifespan_min)

    return jwt.encode(
        payload.dict(),
        secret,
        algorithm=ALGORITHM,
    )


def token_is_authenticated(token: str, secret: str) -> bool:
    payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    original_token = jwt.encode(payload, secret, ALGORITHM)

    return True if token == original_token else False


def validate_jwt(token: str, secret: str) -> None:
    try:
        jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.exceptions.DecodeError:
        raise TOKEN_DECODE_EXCEPTION
    except jwt.ExpiredSignatureError:
        raise EXPIRED_TOKEN_SIGNATURE_EXCEPTION

    if not token_is_authenticated(token, secret):
        raise MALFORMED_TOKEN_EXCEPTION


def hash_password(pw: str) -> str:
    hashed_pw = bcrypt.hashpw(
        pw.encode("utf-8"),
        salt=bcrypt.gensalt(),
    )

    return hashed_pw.decode("utf-8")


def passwords_match(plain_pw: str, hashed_pw: str) -> bool:
    return bcrypt.checkpw(
        plain_pw.encode("utf-8"),
        hashed_pw.encode("utf-8"),
    )


def get_payload_from_jwt(token: str, secret: str) -> dict:
    return jwt.decode(token, secret, algorithms=[ALGORITHM])
