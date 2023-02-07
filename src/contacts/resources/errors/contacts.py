from fastapi import HTTPException


CONTACT_DOES_NOT_EXIST_EXCEPTION = HTTPException(
    status_code=404, 
    detail="Contact doesn't exist",
)
PHONE_NUM_FORMAT_EXCEPTION = HTTPException(
    status_code=422, 
    detail="Invalid phone number format"
)
PHONE_NUM_LEN_EXCEPTION = HTTPException(
    status_code=422,
    detail="Invalid phone number length",
)
USER_HAS_PHONE_NUM_EXCEPTION = HTTPException(
    status_code=409,
    detail="User already has contact with such number",
)
ORDER_PARAMS_EXCEPTION = HTTPException(
    status_code=400,
    detail="Incorrect order parameters",
)
