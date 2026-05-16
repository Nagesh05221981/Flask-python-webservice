from typing import Optional, List

from pydantic import BaseModel, EmailStr


# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# --- User ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    api_key: str

    model_config = {"from_attributes": True}


# --- Product ---
class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: float
    in_stock: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    in_stock: bool
    owner_id: int

    model_config = {"from_attributes": True}


# --- OAuth ---
class OAuthCallbackRequest(BaseModel):
    code: str
