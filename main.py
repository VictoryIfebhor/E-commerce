from typing import List, Optional, Type

from fastapi import FastAPI
from tortoise import BaseDBAsyncClient
from tortoise.contrib.fastapi import register_tortoise
from tortoise.signals import post_save

from authentication import hash_password
from models import Business, User, User_Pydantic, UserIn_Pydantic

app = FastAPI()


@post_save(User)
async def register_business(
    sender: Type[User], instance: User, created: bool,
    using_db: Optional[BaseDBAsyncClient], update_fields: List[str]
):
    # create a business account for the user
    if created:
        await Business.create(name=instance.username, owner=instance)


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

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
