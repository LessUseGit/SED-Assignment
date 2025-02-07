from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[String] = mapped_column(String, unique=True, index=True)
    email: Mapped[String] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[String] = mapped_column(String)
    is_admin: Mapped[Boolean] = mapped_column(Boolean, default=False)
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)

    assets = relationship("Asset", back_populates="owner")


class Asset(Base):
    __tablename__ = "assets"

    asset_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[String] = mapped_column(String, index=True)
    serial_number: Mapped[String] = mapped_column(String, unique=True, nullable=False)
    type: Mapped[String] = mapped_column(String)
    status: Mapped[String] = mapped_column(String, default="Active")
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"))

    owner = relationship("User", back_populates="assets")
