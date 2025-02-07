from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.crud import asset_crud
from app.crud.user_crud import get_user_by_email
from app.database.database import get_db
from app.middleware import add_flash_message
from app.schemas.asset_schemas import AssetCreate, AssetUpdate

assets_router = APIRouter(prefix="/assets")


@assets_router.post("/add")
def add_asset(
    request: Request,
    name: str = Form(...),
    serial_number: str = Form(...),
    type: str = Form(...),
    owner_email: EmailStr = Form(...),
    db: Session = Depends(get_db),
):
    new_owner = get_user_by_email(db=db, email=owner_email)
    if not new_owner:
        add_flash_message(request, "User not found", category="warning")
        return RedirectResponse(url="/dashboard", status_code=302)

    try:
        asset_crud.create_asset(
            db=db,
            new_asset=AssetCreate(
                name=name,
                serial_number=serial_number,
                type=type,
                owner_id=new_owner.user_id
            ),
        )
    except:
        add_flash_message(request, "Failed to add asset", category="danger")
    else:
        add_flash_message(request, "Asset added successfully", category="success")

    return RedirectResponse(url="/dashboard", status_code=302)


@assets_router.get("/getById")
def get_asset_by_id(asset_id: int, db: Session = Depends(get_db)):
    return asset_crud.get_asset_by_id(db=db, asset_id=asset_id)


@assets_router.post("/update/{asset_id}")
def update_asset(
    request: Request,
    asset_id: int,
    name: str = Form(...),
    serial_number: str = Form(...),
    type: str = Form(...),
    status: str = Form(...),
    owner_email: EmailStr = Form(...),
    db: Session = Depends(get_db),
):
    new_owner_id = None
    if owner_email:
        new_owner = get_user_by_email(db=db, email=owner_email)
        if not new_owner:
            add_flash_message(request, "User not found", category="warning")
            return RedirectResponse(url="/dashboard", status_code=302)        
        new_owner_id = new_owner.user_id

    updated_asset = AssetUpdate(
        name=name,
        serial_number=serial_number,
        type=type,
        status=status,
        owner_id=new_owner_id
    )

    try:
        asset_crud.update_asset(db=db, asset_id=asset_id, asset_update=updated_asset)
    except:
        add_flash_message(request, "Failed to update asset", category="danger")
    else:
        add_flash_message(request, "Asset successfully updated", category="success")

    return RedirectResponse(url="/dashboard", status_code=302)


@assets_router.post("/delete/{asset_id}")
def delete_asset(request: Request, asset_id: int, db: Session = Depends(get_db)):
    try:
        asset_crud.delete_asset(db=db, asset_id=asset_id)
    except:
        add_flash_message(request, "Failed to delete asset", category="danger")
    else:
        add_flash_message(request, "Asset successfully deleted", category="success")
    return RedirectResponse(url="/dashboard", status_code=302)
