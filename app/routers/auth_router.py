from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app import auth
from app.database.database import get_db
from app.crud import user_crud
from app.middleware import add_flash_message, get_flash_messages
from app.schemas.user_schemas import UserCreate

auth_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@auth_router.get("/login")
def get_login_page(request: Request):
    flash_messages = get_flash_messages(request)
    return templates.TemplateResponse(
        request=request, name="login.html", context={"flash_messages": flash_messages}
    )


@auth_router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = auth.authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = auth.create_access_token(data={"sub": user.email})

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    response.headers["Location"] = "/dashboard"
    response.status_code = 302
    return response


@auth_router.get("/logout")
async def logout(request: Request):
    add_flash_message(request, "Logout successful", category="success")
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response


@auth_router.get("/register")
def get_register_page(request: Request):
    flash_messages = get_flash_messages(request)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"flash_messages": flash_messages},
    )


@auth_router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    is_admin: bool = Form(...),
    db: Session = Depends(get_db),
):
    # Basic password confirmation validation
    if password != confirm_password:
        add_flash_message(request, "Passwords do not match", category="warning")
        return RedirectResponse(url="/register", status_code=303)

    # Check if user with email already exists
    existing_user_email = user_crud.get_user_by_email(db, email=email)
    if existing_user_email:
        add_flash_message(
            request, "User with that email already exists", category="warning"
        )
        return RedirectResponse(url="/register", status_code=303)

    # Check if user with that username already exists
    existing_username = user_crud.get_user_by_username(db, username=username)
    if existing_username:
        add_flash_message(
            request, "User with that username already exists", category="warning"
        )
        return RedirectResponse(url="/register", status_code=303)
    
    try:
        user_crud.create_user(
            db=db,
            user=UserCreate(
                username=username, email=email, password=password, is_admin=is_admin
            ),
        )
    except:
        add_flash_message(request, "Failed to register", category="danger")
    else:
        add_flash_message(request, "Successfully registered", category="success")

    return RedirectResponse(url="/login", status_code=308)
