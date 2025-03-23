from app.crud.asset_crud import create_asset, get_asset_by_serial_number
from app.crud.user_crud import create_user, get_user_by_email
from app.database.database import SessionLocal
from app.schemas.asset_schemas import AssetCreate
from app.schemas.user_schemas import UserCreate


def create_default_users():
    db = SessionLocal()

    try:
        if not get_user_by_email(db, "admin@example.com"):
            admin_data = UserCreate(
                username="admin",
                email="admin@example.com",
                password="password123",
                is_admin=True,
            )
            create_user(db, user=admin_data)
            print("Admin user created")

        if not get_user_by_email(db, "regular@example.com"):
            regular_data = UserCreate(
                username="regular",
                email="regular@example.com",
                password="password123",
                is_admin=False,
            )
            create_user(db, user=regular_data)
            print("Regular user created")
    finally:
        db.close()

def create_default_assets():
    db = SessionLocal()
    try:
        admin_user = get_user_by_email(db, "admin@example.com")
        regular_user = get_user_by_email(db, "regular@example.com")

        if not admin_user or not regular_user:
            print("Default users not found. Ensure users are created before assets.")
            return

        default_assets = [
            {
                "name": "Dell Laptop",
                "serial_number": "DL123456",
                "type": "Laptop",
                "status": "Active",
                "owner_id": admin_user.user_id,
            },
            {
                "name": "HP Laptop",
                "serial_number": "HP987654",
                "type": "Laptop",
                "status": "Active",
                "owner_id": regular_user.user_id,
            },
            {
                "name": "iPhone 13",
                "serial_number": "IP130001",
                "type": "Smartphone",
                "status": "Active",
                "owner_id": admin_user.user_id,
            },
            {
                "name": "Samsung Galaxy S22",
                "serial_number": "SGS22002",
                "type": "Smartphone",
                "status": "Active",
                "owner_id": regular_user.user_id,
            },
            {
                "name": "Dell Monitor",
                "serial_number": "DM555666",
                "type": "Monitor",
                "status": "Active",
                "owner_id": admin_user.user_id,
            },
            {
                "name": "Logitech Mouse",
                "serial_number": "LM333777",
                "type": "Peripheral",
                "status": "Active",
                "owner_id": regular_user.user_id,
            },
        ]

        for asset in default_assets:
            existing_asset = (
                get_asset_by_serial_number(db, asset["serial_number"])
            )
            if not existing_asset:
                create_asset(
                    db=db,
                    new_asset=AssetCreate(
                        name=asset["name"],
                        serial_number=asset["serial_number"],
                        type=asset["type"],
                        status=asset["status"],
                        owner_id=asset["owner_id"],
                    ),
                )
                print(f"Asset '{asset['name']}' created.")
            else:
                print(f"Asset '{asset['name']}' already exists.")

    finally:
        db.close()