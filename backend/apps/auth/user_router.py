from ..common import UserAuthParams
from fastapi import APIRouter, Depends
from .schema import UserSchema
from .models import User
from typing import List

router: APIRouter = APIRouter()


@router.get("/", response_model=List[UserSchema])
async def list_users(common: UserAuthParams = Depends(UserAuthParams)):
    users = User.objects.all()
    return users
