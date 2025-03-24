from fastapi import APIRouter, Depends, Request
from fastapi.params import Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.crud import asset_crud, user_crud
from app.database.database import get_db
from app.database.models import User
from app.middleware import add_flash_message, get_flash_messages
from app.schemas.user_schemas import UserCreate, UserUpdate

users_router = APIRouter(prefix="/users")
templates = Jinja2Templates(directory="app/templates")


@users_router.get("/management")
def user_management(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    flash_messages = get_flash_messages(request)

    return templates.TemplateResponse(
        request=request,
        name="user_management.html",
        context={
            "flash_messages": flash_messages,
            "user": current_user,
            "users": user_crud.get_users(db=db),
        },
    )


@users_router.get("/profile")
def profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_assets = asset_crud.get_asset_by_owner_id(db=db, owner_id=current_user.user_id)

    flash_messages = get_flash_messages(request)

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "flash_messages": flash_messages,
            "user": current_user,
            "user_assets": user_assets,
        },
    )


@users_router.post("/add")
def add_user(
    request: Request,
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    is_admin: bool = Form(...),
    is_active: bool = Form(...),
    db: Session = Depends(get_db),
):
    # Basic password confirmation validation
    if password != confirm_password:
        add_flash_message(request, "Passwords do not match", category="warning")
        return RedirectResponse(url="/users/management", status_code=302)

    # Check if user with email already exists
    existing_user_email = user_crud.get_user_by_email(db, email=email)
    if existing_user_email:
        add_flash_message(
            request, "User with this email already exists", category="warning"
        )
        return RedirectResponse(url="/users/management", status_code=302)

    # Check if user with that username already exists
    existing_username = user_crud.get_user_by_username(db, username=username)
    if existing_username:
        add_flash_message(
            request, "User with this username already exists", category="warning"
        )
        return RedirectResponse(url="/users/management", status_code=302)

    try:
        user_crud.create_user(
            db=db,
            user=UserCreate(
                username=username, email=email, password=password, is_admin=is_admin
            ),
        )
    except:
        add_flash_message(request, "Failed to add user", category="danger")
    else:
        add_flash_message(request, "User added successfully", category="success")

    return RedirectResponse(url="/users/management", status_code=302)


@users_router.post("/update/{user_id}")
def update_user(
    request: Request,
    user_id: int,
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str|None = Form(...),
    confirm_password: str|None = Form(...),
    is_admin: bool|None = Form(...),
    is_active: bool = Form(...),
    db: Session = Depends(get_db),
):
    existing_user = user_crud.get_user_by_id(db, user_id)

    if not existing_user:
        add_flash_message(request, "User not found", category="danger")
        return RedirectResponse(url="/users/management", status_code=302)

    if (
        existing_user.username == username
        and existing_user.email == email
        and (password is None or password == "")
        and existing_user.is_admin == is_admin
        and existing_user.is_active == is_active
    ):
        add_flash_message(request, "No changes were made", category="warning")
        return RedirectResponse(url="/users/management", status_code=302)


    if password and password != confirm_password:
        add_flash_message(request, "Passwords do not match", category="danger")
        return RedirectResponse(url="/users/management", status_code=302)
    
    if password and len(password) < 8:
        add_flash_message(request, "Password doesn't meet criteria", category="danger")
        return RedirectResponse(url="/users/management", status_code=302)

    updated_user = UserUpdate(
        username=username,
        email=email,
        password=password if password else None,
        is_admin=is_admin,
        is_active=is_active,
    )

    try:
        user_crud.update_user(db=db, user_id=user_id, user_update=updated_user)
        print(updated_user)
    except:
        add_flash_message(request, "Failed to update user", category="danger")
    else:
        add_flash_message(request, "User successfully updated", category="success")

    return RedirectResponse(url="/users/management", status_code=302)


@users_router.post("/delete/{user_id}")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    try:
        user_crud.delete_user(db=db, user_id=user_id)
    except:
        add_flash_message(request, "Failed to delete user", category="danger")
    else:
        add_flash_message(request, "User deleted successfully", category="success")
    return RedirectResponse(url="/users/management", status_code=302)
