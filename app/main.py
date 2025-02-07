from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.routers import auth_router, assets_router, main_router, users_router
from app.database.database import Base, engine

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

SECRET = "super-secret-key"

Base.metadata.create_all(bind=engine)

app.include_router(main_router.main_router)
app.include_router(auth_router.auth_router)
app.include_router(assets_router.assets_router)
app.include_router(users_router.users_router)
