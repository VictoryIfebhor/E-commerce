import jwt

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from pydantic import BaseModel, EmailStr
from typing import List
from .models import User

config_credentials = dotenv_values(".env")
print(config_credentials)
print(config_credentials["SECRET"])

# create configuration for the fastapi-mail
conf = ConnectionConfig(
    MAIL_USERNAME=config_credentials["EMAIL"],
    MAIL_PASSWORD=config_credentials["PASSWORD"],
    MAIL_FROM=config_credentials["EMAIL"],
    MAIL_PORT=587,
    MAIL_SERVER="smpt.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True
)


# create the email schema
class EmailSchema(BaseModel):
    email: List[EmailStr]


# create the body of the message
TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
    </head>
    <body>
        <div>
            <h3>Account Verification</h3>
            <br>

            <p>Thank you for choosing our e-commerce services. Click the button below to verify your account.</p>
            <a href="http://127.0.0.1:8000/verification?token={}"><button>Verify</button></a>

            <p>If you do not recognise any activity like this, kindly ignore the email.</p>
        </div>
    </body>
    </html>
"""


# create the function to send the mail
async def send_email(email: EmailSchema, instance: User):
    token_data = {
        "id": instance.id,
        "username": instance.username
    }

    token = jwt.encode(token_data, config_credentials["SECRET"])

    message = MessageSchema(
        subject="Email Verification of account",
        recipients=email,
        body=TEMPLATE.format(token),
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
