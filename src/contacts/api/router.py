from fastapi import APIRouter

from contacts.api import auth, contacts, users


router = APIRouter()
router.include_router(auth.router, prefix="/auth")
router.include_router(contacts.router, prefix="/contacts")
router.include_router(users.router, prefix="/users")
