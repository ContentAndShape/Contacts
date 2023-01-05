from datetime import datetime, timedelta

import jwt
import bcrypt


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


def validate_jwt(token: str, secret: str) -> dict:
    """Validates jwt and returns status code, detail and payload"""
    response = {
        "status_code": 400,
        "detail": "bad request",
        "payload": None,
    }

    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.exceptions.DecodeError:
        response["detail"] = "token decode error"
        return response
    except jwt.ExpiredSignatureError:
        response["detail"] = "expired token"
        return response

    if not token_is_authenticated(token, secret):
        response["status_code"] = 401
        response["detail"] = "malformed token"
        return response

    response["status_code"] = 200
    response["detail"] = "ok"
    response["payload"] = payload

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
