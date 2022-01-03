from os import stat
from typing import List, Optional, Type

from fastapi import FastAPI, Request, HTTPException, status, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from tortoise import BaseDBAsyncClient
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import DoesNotExist
from tortoise.signals import post_save

from authentication import hash_password, verify_token, generate_token, decode_token
from emailsender import send_email
from models import Business, Business_Pydantic, Product, User, UserIn_Pydantic, UserOut_Pydantic
from file_handler import save_image, delete_image

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")


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


@app.get("/", response_class=RedirectResponse)
async def index():
    return "http://127.0.0.1:8000/docs"


@app.post("/user")
async def register_user(user: UserIn_Pydantic):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = hash_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user: User = await UserOut_Pydantic.from_tortoise_orm(user_obj)

    return {
        "status": "ok",
        "data": f"Hi {new_user.username}, Check your email and click the link to complete registration."
    }


@app.post("/verification", response_class=HTMLResponse, include_in_schema=False)
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


@app.post("/token", include_in_schema=False)
async def generate_user_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await generate_token(request_form.username, request_form.password)

    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_schema)):
    payload = decode_token(token)
    user = await User.get(id=payload["id"])
    user_ = await UserOut_Pydantic.from_tortoise_orm(user)

    return user_


@app.post("/users/me")
async def user_details(user: User = Depends(get_current_user)):
    business = await Business.get(owner=user.id)
    business_ = await Business_Pydantic.from_tortoise_orm(business)

    return {
        "status": "ok",
        "data": {
            "user": user.dict(),
            "business": business_.dict()
        }
    }


@app.post("/image/business")
async def upload_business_image(
    file: UploadFile = File(...), user: User = Depends(get_current_user)
):
    db_filename = await save_image(file)

    business = await Business.get(owner=user.id)
    delete_image(business.logo)
    business.logo = db_filename
    await business.save()

    return {"status": "ok", "message": "Successfully uploaded image."}


@app.post("/image/product/{id}")
async def upload_product_image(
    id: int, file: UploadFile = File(...), user: User = Depends(get_current_user)
):
    db_filename = await save_image(file)

    try:
        product = await Product.get(id=id)
    except DoesNotExist:
        delete_image(db_filename)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product does not exist"
        )

    business = await Business.get(id=product.business)

    if user.id != business.owner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated to perform this action.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    delete_image(product.image)
    product.image = db_filename
    await product.save()

    return {"status": "ok", "message": "Successfully uploaded image."}

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
