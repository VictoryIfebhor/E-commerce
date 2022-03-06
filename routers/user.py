from typing import Type, Optional, List

from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from fastapi_mail.errors import ConnectionErrors as MailConnectionError
from tortoise import BaseDBAsyncClient
from tortoise.signals import post_save

from security_tools import hash_password
from dependencies import get_current_user
from application_tools import send_email
from models import (
    Business,
    Business_Pydantic,

    User,
    UserIn_Pydantic,
    UserOut_Pydantic
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@post_save(User)
async def register_business(
    sender: Type[User], instance: User, created: bool,
    using_db: Optional[BaseDBAsyncClient], update_fields: List[str]
):
    # create a business account for the user
    if created:
        business = await Business.create(
            name=instance.username,
            owner=instance
        )

    # send verification email to user
    try:
        await send_email([instance.email], instance)
    except MailConnectionError as e:
        print(e)
        # If there was any error while sending email, delete user and business
        # This is so the user can register again
        await business.delete()
        await instance.delete()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Could not send verification mail to user."
                "Register again later."
            )
        )


@router.post("/user", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserIn_Pydantic):
    """
    Create a user with the following information.
    - **username**: A name that will be unique to the user.
    - **password**: Something to validate or authenticate the user.
    - **email**: A valid email address that belongs to the user.
    """
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = hash_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user: User = await UserOut_Pydantic.from_tortoise_orm(user_obj)

    return {
        "status": "ok",
        "data": (
            f"Hi {new_user.username}, "
            "Check your email and click the link to complete registration."
        )
    }


@router.get("/me")
async def user_details(user: User = Depends(get_current_user)):
    business = await Business.get(owner=user.id)
    business_ = await Business_Pydantic.from_tortoise_orm(business)

    return {
        "status": "ok",
        "data": {
            "user": user,
            "business": business_.dict()
        }
    }
