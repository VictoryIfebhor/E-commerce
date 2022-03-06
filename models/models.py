from datetime import datetime

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class User(models.Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(null=False, unique=True, max_length=20)
    email = fields.CharField(null=False, unique=True, max_length=200)
    password = fields.CharField(null=False, max_length=100)
    is_verified = fields.BooleanField(null=False, default=False)
    date_joined = fields.DatetimeField(null=False, default=datetime.utcnow)


class Business(models.Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(null=False, unique=True, max_length=20)
    city = fields.CharField(null=False, default="Unspecified", max_length=100)
    region = fields.CharField(
        null=False, default="Unspecified", max_length=100
    )
    description = fields.TextField(null=True)
    logo = fields.CharField(null=False, default="default.jpg", max_length=200)
    owner = fields.ForeignKeyField("models.User", related_name="business")


class Product(models.Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(null=False, index=True, max_length=100)
    category = fields.CharField(index=True, max_length=30)
    original_price = fields.DecimalField(max_digits=12, decimal_places=2)
    current_price = fields.DecimalField(max_digits=12, decimal_places=2)
    discount = fields.IntField()
    discount_expiry_date = fields.DateField(default=datetime.utcnow)
    image = fields.CharField(
        null=False, default="defaultproduct.jpg", max_length=200
    )
    business = fields.ForeignKeyField(
        "models.Business", related_name="products"
    )


User_Pydantic = pydantic_model_creator(
    User,
    name="User"
)
UserIn_Pydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude_readonly=True,
    exclude=("is_verified", "date_joined")
)
UserOut_Pydantic = pydantic_model_creator(
    User,
    name="UserOut",
    exclude=("password",)
)

Business_Pydantic = pydantic_model_creator(
    Business,
    name="Business"
)
BusinessIn_Pydantic = pydantic_model_creator(
    Business,
    name="BusinessIn",
    exclude_readonly=True
)

Product_Pydantic = pydantic_model_creator(
    Product,
    name="Product"
)
ProductIn_Pydantic = pydantic_model_creator(
    Product,
    name="ProductIn",
    exclude_readonly=True,
    exclude=("discount", "image")
)
