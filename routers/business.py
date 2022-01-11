from fastapi import APIRouter, UploadFile, File, Depends

from dependencies import get_current_user
from file_handler import delete_image, save_image
from models import Business, User

router = APIRouter(
    prefix="/business",
    tags=["Business"]
)


@router.post("/image")
async def upload_business_image(
    file: UploadFile = File(...), user: User = Depends(get_current_user)
):
    db_filename = await save_image(file)

    business = await Business.get(owner=user.id)
    delete_image(business.logo)
    business.logo = db_filename
    await business.save()

    return {"status": "ok", "message": "Successfully uploaded image."}
