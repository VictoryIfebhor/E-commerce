from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from security_tools import decode_token
from models import User, UserOut_Pydantic

router = APIRouter(prefix="/authenticate")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_schema)):
    payload = decode_token(token)
    user = await User.get(id=payload["id"])
    user_ = await UserOut_Pydantic.from_tortoise_orm(user)

    return user_
