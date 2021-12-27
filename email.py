# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, config
from dotenv import dotenv_values
# from pydantic import BaseModel, EmailStr
# from typing import List
# from .models import User

config_credentials = dotenv_values(".env")
print(config_credentials)
print(config_credentials["SECRET"])

# conf = ConnectionConfig(
#     MAIL_USERNAME=config_credentials["EMAIL"],
#     MAIL_PASSWORD=config_credentials["PASSWORD"],
#     MAIL_FROM=config_credentials["EMAIL"],
#     MAIL_PORT=587,
#     MAIL_SERVER="smpt.gmail.com",
#     MAIL_TLS=True,
#     MAIL_SSL=False,
#     USE_CREDENTIALS=True
# )


# class EmailSchema(BaseModel):
#     email: List[EmailStr]


# async def send_email(email: List, instance: User):
#     token = {
#         "id": instance.id,
#         "username": instance.username
#     }

