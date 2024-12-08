from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.models import User
from app.core.security.user import get_current_active_user
from app.schemas.user import UserOut

router = APIRouter(
    tags=["users"]
)


@router.get("/users/me/")
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserOut:
    return current_user
