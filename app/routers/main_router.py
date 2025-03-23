from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.crud.asset_crud import get_assets
from app.crud.user_crud import get_email_from_user_id
from app.database.database import get_db
from app.database.models import User
from app.middleware import add_flash_message, get_flash_messages

# Set up the router and templates
main_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@main_router.get("/dashboard")
def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assets_list = get_assets(db=db)
    for asset in assets_list:
        asset.owner_email = get_email_from_user_id(db=db, user_id=asset.owner_id)

    flash_messages = get_flash_messages(request)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "flash_messages": flash_messages,
            "user": current_user,
            "assets": assets_list,
        },
    )


@main_router.get("/health")
@main_router.head("/health")
def health():
    return {"msg": "hello world :)"}


@main_router.get("/")
def root(request: Request):
    return templates.TemplateResponse(request=request, name="root.html")
