from datetime import datetime, timedelta

import jwt
import bcrypt


JWT_EXP_DELTA_MIN = 60 * 24


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
    )


def jwt_is_valid(token: str, secret: str) -> bool:
    try:
        jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return False

    return True


def hash_password(pw: str) -> str:
    hashed_pw = bcrypt.hashpw(
        pw.encode('utf-8'),
        salt = bcrypt.gensalt(),
    )
    
    return hashed_pw.decode('utf-8')


def passwords_match(plain_pw: str, hashed_pw: str) -> bool:
    return bcrypt.checkpw(
        plain_pw.encode('utf-8'),
        hashed_pw.encode('utf-8'),
    )
