import jwt

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from typing import List
from models import User

config_credentials = dotenv_values(".env")

# create configuration for the fastapi-mail
conf = ConnectionConfig(
    MAIL_USERNAME=config_credentials["EMAIL"],
    MAIL_PASSWORD=config_credentials["PASSWORD"],
    MAIL_FROM=config_credentials["EMAIL"],
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER="./templates"
)


# create the function to send the mail
async def send_email(email: List[str], instance: User):
    token_data = {
        "id": instance.id,
        "username": instance.username
    }

    SECRET = config_credentials["SECRET"]
    if SECRET:
        body = {
            "token": jwt.encode(
                token_data, SECRET, algorithm="HS256"
            ),
            "base_url": "http://127.0.0.1:8000"
        }
    else:
        raise Exception("No secret key to encode token")

    message = MessageSchema(
        subject="Email Verification of account",
        recipients=email,
        template_body=body
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="verification.html")
