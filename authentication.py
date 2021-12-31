import jwt

from dotenv import dotenv_values
from fastapi import status, HTTPException
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist

from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
config_credential = dotenv_values(".env")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, config_credential["SECRET"], algorithms=["HS256"])
        user = User.get(id=payload["id"])
        print(type(user))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user
