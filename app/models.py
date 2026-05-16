import secrets

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    api_key = Column(String, unique=True, index=True, default=lambda: secrets.token_urlsafe(32))

    products = relationship("Product", back_populates="owner")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, default="")
    price = Column(Float, nullable=False)
    in_stock = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="products")
