from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File
from tortoise.exceptions import DoesNotExist

from dependencies import get_current_verified_user
from application_tools import delete_image, save_image
from models import (
    Product_Pydantic,
    User,
    Business,
    Product,
    ProductIn_Pydantic,
    Business_Pydantic
)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_new_product(
    product: ProductIn_Pydantic,
    user: User = Depends(get_current_verified_user)
):
    product = product.dict(exclude_unset=True)

    # calculate discount
    current_price = product["current_price"]
    original_price = product["original_price"]
    if current_price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The current price set for the product is less than 0.",
        )

    if original_price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The original price set for the product is not acceptable. "
                "Original price has to be greater than 0."
            )
        )

    discount = ((original_price - current_price) / original_price) * 100
    product["discount"] = round(discount)

    # set business for the product
    business = await Business.get(owner=user.id)
    product["business"] = business
    business = await Business_Pydantic.from_tortoise_orm(business)

    await Product.create(**product)

    return {"status": "ok", "message": "Successfully added new product"}


@router.get("/")
async def get_all_products():
    response = await Product_Pydantic.from_queryset(Product.all())
    return {"status": "ok", "data": response}


@router.get("/{id}")
async def get_product_by_id(id: int):
    response = await Product.get(id=id)
    business = await response.business
    product = await Product_Pydantic.from_tortoise_orm(response)
    business_out = await Business_Pydantic.from_tortoise_orm(business)

    return {
        "product": product,
        "business": business_out
    }


@router.delete("/{id}")
async def delete_product(
    id: int,
    user: User = Depends(get_current_verified_user)
):
    business = await Business.get(owner=user.id)
    product = await Product.get(id=id)
    product_business = await product.business

    if product_business == business:
        await product.delete()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Deleting of products not owned by you is forbidden.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"status": "ok", "message": "Successfully deleted product"}


@router.post("/{id}/image")
async def upload_product_image(
    id: int,
    file: UploadFile = File(...),
    user: User = Depends(get_current_verified_user)
):
    try:
        product = await Product.get(id=id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product does not exist"
        )

    business: Business = await product.business
    owner: User = await business.owner

    if user.id != owner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Uploading images of products not owned by you is forbidden."
            ),
            headers={"WWW-Authenticate": "Bearer"}
        )

    db_filename = await save_image(file)

    delete_image(product.image)
    product.image = db_filename
    await product.save()

    return {"status": "ok", "message": "Successfully uploaded image."}
