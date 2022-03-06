from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from tortoise.contrib.fastapi import register_tortoise

from routers import auth, business, product, user

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(product.router)
app.include_router(business.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def index():
    return "http://127.0.0.1:8000/docs"


register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
