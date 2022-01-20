from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from tortoise.contrib.fastapi import register_tortoise

from security_tools import verify_token, generate_token
from routers import business, product, user

app = FastAPI()

app.include_router(user.router)
app.include_router(product.router)
app.include_router(business.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def index():
    return "http://127.0.0.1:8000/docs"


@app.post("/token", tags=["Authentication"])
async def generate_user_token(request_form: OAuth2PasswordRequestForm = Depends()):
    """
    End point to login or authenticate a user.
    - The only parameters needed are the username and password.
    - The username and password should be passed in a form.
    """
    token = await generate_token(request_form.username, request_form.password)

    return {"access_token": token, "token_type": "bearer"}


@app.get("/verification/{token}", response_class=HTMLResponse, include_in_schema=False)
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
