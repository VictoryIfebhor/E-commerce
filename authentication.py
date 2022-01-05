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


async def verify_token(token: str):
    try:
        payload = decode_token(token)
        user = await User.get(id=payload["id"])
        print(type(user))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


async def generate_token(username: str, password: str):
    try:
        user = await User.get(username=username)
        password_correct = pwd_context.verify(password, user.password)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token_data = {
        "id": user.id,
        "username": user.username
    }

    return jwt.encode(token_data, config_credential["SECRET"], algorithm="HS256")


def decode_token(token: str):
    return jwt.decode(token, config_credential["SECRET"], algorithms=["HS256"])
