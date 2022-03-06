from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from security_tools import generate_token, verify_token

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/token")
async def generate_user_token(
    request_form: OAuth2PasswordRequestForm = Depends()
):
    """
    End point to login or authenticate a user.
    - The only parameters needed are the username and password.
    - The username and password should be passed in a form.
    """
    token = await generate_token(request_form.username, request_form.password)

    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/verification/{token}",
    response_class=HTMLResponse,
    include_in_schema=False
)
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
