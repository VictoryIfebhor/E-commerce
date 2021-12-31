from typing import List, Optional, Type

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from tortoise import BaseDBAsyncClient
from tortoise.contrib.fastapi import register_tortoise
from tortoise.signals import post_save

from authentication import hash_password, verify_token
from emailsender import send_email
from models import Business, User, User_Pydantic, UserIn_Pydantic

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@post_save(User)
async def register_business(
    sender: Type[User], instance: User, created: bool,
    using_db: Optional[BaseDBAsyncClient], update_fields: List[str]
):
    # create a business account for the user
    if created:
        await Business.create(name=instance.username, owner=instance)

    # send verification email to user
    await send_email([instance.email], instance)


@app.get("/")
async def index():
    return {"Message": "Hello World"}


@app.post("/user")
async def register_user(user: UserIn_Pydantic):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = hash_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user: User = await User_Pydantic.from_tortoise_orm(user_obj)

    return {
        "status": "ok",
        "data": f"Hi {new_user.username}, Check your email and click the link to complete registration."
    }


@app.post("/verification", response_class=HTMLResponse)
async def send_confirmation_email(token: str, request: Request):
    user = await verify_token(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        params = {"request": request, "username": user.username}

        return templates.TemplateResponse("confirmation.html", params)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
