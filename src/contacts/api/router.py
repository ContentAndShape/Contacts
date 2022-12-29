from fastapi import APIRouter

from contacts.api import auth, contacts


router = APIRouter()
router.include_router(auth.router, prefix="/auth")
router.include_router(contacts.router, prefix="/contacts")
