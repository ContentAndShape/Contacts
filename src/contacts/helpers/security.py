from datetime import datetime, timedelta

import jwt
import bcrypt


JWT_EXP_DELTA_MIN = 60 * 24
ALGORITHM = "HS256"


def get_jwt(
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


def jwt_expired(token: str, secret: str) -> bool:
    try:
        jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return True

    return False


def get_payload_from_jwt(token: str, secret: str) -> dict | None:
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.exceptions.DecodeError or jwt.ExpiredSignatureError:
        return None

    return payload


def jwt_is_valid(token: str, secret: str) -> bool:
    payload = get_payload_from_jwt(token=token, secret=secret)

    if payload is None:
        return False

    valid_token = jwt.encode(payload, secret, ALGORITHM)

    return True if token == valid_token else False


def validate_jwt(token: str, secret: str) -> dict:
    """Validates jwt and returns corresponding status code with details"""
    response = {
        "status_code": 200,
        "detail": "ok",
    }

    if not jwt_is_valid(token=token, secret=secret):
        response["status_code"] = 401
        response["detail"] = "malformed token"
        return response

    if jwt_expired(token=token, secret=secret):
        response["status_code"] = 401
        response["detail"] = "token expired"
        return response

    return response


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
