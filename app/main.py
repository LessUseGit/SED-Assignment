from jose import ExpiredSignatureError
from fastapi import FastAPI, HTTPException
from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth_router, assets_router, main_router, users_router
from app.database.database import Base, engine
from app.error_handlers import expired_token_handler, auth_exception_handler

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

app.add_exception_handler(ExpiredSignatureError, expired_token_handler)
app.add_exception_handler(HTTPException, auth_exception_handler)

SECRET = "super-secret-key"

Base.metadata.create_all(bind=engine)

app.include_router(main_router.main_router)
app.include_router(auth_router.auth_router)
app.include_router(assets_router.assets_router)
app.include_router(users_router.users_router)
