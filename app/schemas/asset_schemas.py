from typing import Optional
from pydantic import BaseModel


class AssetBase(BaseModel):
    name: str
    serial_number: str
    type: str
    status: str = "Active"


class AssetCreate(AssetBase):
    owner_id: int


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    serial_number: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[int] = None


class AssetRead(AssetBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
