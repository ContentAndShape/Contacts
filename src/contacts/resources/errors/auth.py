from fastapi import HTTPException


NO_TOKEN_EXCEPTION = HTTPException(
    status_code=400,
    detail="No token provided",
)
TOKEN_DECODE_EXCEPTION = HTTPException(
    status_code=400,
    detail="Token decode error",
)
EXPIRED_TOKEN_SIGNATURE_EXCEPTION = HTTPException(
    status_code=400,
    detail="Expired token signature",
)
MALFORMED_TOKEN_EXCEPTION = HTTPException(
    status_code=401,
    detail="Malformed token",
)
INCORRECT_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=401,
    detail="Incorrect username or password",
)
