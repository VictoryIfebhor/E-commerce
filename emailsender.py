import jwt

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from pydantic import EmailStr
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
    USE_CREDENTIALS=True
)


# create the body of the message
TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    </head>
    <body>
        <div>
            <form method="post" action="/verification?token={token}">
                <h3>Account Verification</h3>
                <br>

                <p>Thank you for choosing our e-commerce services. Click the button below to verify your account.</p>
                <input type="submit" value="Verify">

                <p>If you do not recognise any activity like this, kindly ignore the email.</p>
            </form>
        </div>
    </body>
    </html>
"""


# create the function to send the mail
async def send_email(email: List[EmailStr], instance: User):
    token_data = {
        "id": instance.id,
        "username": instance.username
    }

    token = jwt.encode(token_data, config_credentials["SECRET"], algorithm="HS256")

    message = MessageSchema(
        subject="Email Verification of account",
        recipients=email,
        body=TEMPLATE.format(token=token),
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
