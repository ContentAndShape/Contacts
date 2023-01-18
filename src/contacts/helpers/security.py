from datetime import datetime, timedelta
import jwt
import bcrypt

from fastapi import HTTPException


JWT_EXP_DELTA_MIN = 60 * 24
ALGORITHM = "HS256"


def generate_jwt(
    payload: dict,
    subject: str,
    lifespan_min: int,
    secret: str,
) -> str:
    payload["sub"] = subject
    payload["exp"] = datetime.utcnow() + timedelta(minutes=lifespan_min)

    return jwt.encode(
        payload,
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
        raise HTTPException(status_code=400, detail="token decode error")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="expired token signature")

    if not token_is_authenticated(token, secret):
        raise HTTPException(status_code=401, detail="malformed token")


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
