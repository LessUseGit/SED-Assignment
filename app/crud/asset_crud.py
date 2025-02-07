from sqlalchemy.orm import Session
from app.database.models import Asset
from app.schemas.asset_schemas import AssetCreate, AssetUpdate


def get_asset_by_id(db: Session, asset_id: int):
    return db.query(Asset).filter(Asset.asset_id == asset_id).first()


def get_asset_by_owner_id(db: Session, owner_id: int):
    return db.query(Asset).filter(Asset.owner_id == owner_id).all()


def get_assets(db: Session):
    return db.query(Asset).all()


def create_asset(db: Session, new_asset: AssetCreate):
    db_asset = Asset(
        name=new_asset.name,
        serial_number=new_asset.serial_number,
        type=new_asset.type,
        status=new_asset.status,
        owner_id=new_asset.owner_id,
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


def update_asset(db: Session, asset_id: int, asset_update: AssetUpdate):
    db_asset = get_asset_by_id(db, asset_id)
    if db_asset:
        for key, value in asset_update.dict(exclude_unset=True).items():
            setattr(db_asset, key, value)
        db.commit()
        db.refresh(db_asset)
    return db_asset


def delete_asset(db: Session, asset_id: int):
    db_asset = get_asset_by_id(db, asset_id)
    if db_asset:
        db.delete(db_asset)
        db.commit()
    return db_asset
