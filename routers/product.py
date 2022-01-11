from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File
from tortoise.exceptions import DoesNotExist

from dependencies import get_current_user
from file_handler import delete_image, save_image
from models import User, Business, Product, ProductIn_Pydantic, Business_Pydantic

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post("/product", status_code=status.HTTP_201_CREATED)
async def add_new_product(product: ProductIn_Pydantic, user: User = Depends(get_current_user)):
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


@router.post("/{id}/image")
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
