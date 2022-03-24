import os
import secrets
import shutil

from datetime import datetime

from fastapi import HTTPException, status, UploadFile
from PIL import Image

FILEPATH = "./static/images/"


def get_stamp():
    date_now = str(datetime.now())
    cleaned = date_now.replace(" ", "").replace("-", "").replace(":", "")

    return cleaned[::-1]


async def save_image(file: UploadFile) -> str:
    filename: str = file.filename
    last_position = filename.rfind(".")
    extension = filename[last_position:]

    if extension not in (".png", ".jpg", ".jpeg"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File uploaded should be of type png, jpg or jpeg"
        )

    token_hex = secrets.token_hex(16)
    db_filename = token_hex + get_stamp() + extension
    file_path = FILEPATH + db_filename

    # save image to destination path
    try:
        with open(file_path, "wb") as destination:
            shutil.copyfileobj(file.file, destination)
    finally:
        await file.close()

    # resize image
    with Image.open(file_path) as img:
        img.resize(size=(200, 200))
        img.save(file_path)

    return db_filename


def delete_image(filename: str):
    if filename not in ("default.jpg", "defaultproduct.jpg"):
        try:
            os.remove(FILEPATH + filename)
        except Exception:
            print(f"Failed to delete {filename}.")
