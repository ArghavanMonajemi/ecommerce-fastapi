from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from utils.enums import CartStatus


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    is_admin: bool


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]
    stock: int
    image_url: Optional[str]

    class Config:
        from_attributes = True


class CartItemCreate(BaseModel):
    quantity: int
    product_id: int
    cart_id: int


class CartItemOut(CartItemCreate):
    id: int

    class Config:
        from_attributes = True


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None


class CartCreate(BaseModel):
    user_id: int
    status: CartStatus = CartStatus.OPEN
    items: List[CartItemCreate]
    created_at: datetime
    total_price: float


class CartOut(CartCreate):
    id: int

    class Config:
        from_attributes = True


class CartUpdate(BaseModel):
    status: Optional[CartStatus] = CartStatus.OPEN
    items: Optional[List[CartItemCreate]] = None
    total_price: Optional[float] = None


class AddressCreate(BaseModel):
    user_id: int
    country: str
    city: str
    address: str


class AddressOut(AddressCreate):
    id: int

    class Config:
        from_attributes = True


class AddressUpdate(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
