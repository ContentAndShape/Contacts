from fastapi import HTTPException


USERNAME_EXIST_EXCEPTION = HTTPException(
    status_code=409, 
    detail="Username already exist",
)
USER_ID_EXIST_EXCEPTION = HTTPException(
    status_code=409, 
    detail="User with such id already exist",
)
USER_CONTACT_OWNERSHIP_EXCEPTION = HTTPException(
    status_code=403,
    detail="User doesn't own this contact",
)

