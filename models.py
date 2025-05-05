from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
from utils.enums import CartStatus


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, unique=True)
    first_name = Column(String, nullable=True, index=True)
    last_name = Column(String, nullable=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_modified = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    is_admin = Column(Boolean, nullable=False, default=False)

    carts = relationship("Cart", back_populates="user")
    addresses = relationship("Address", back_populates="user")


class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    created_at = Column(DateTime, index=True, default=func.now, nullable=False)
    status = Column(Enum(CartStatus), default=CartStatus.OPEN, index=True)
    total_price = Column(Float, default=0)

    items = relationship("CartItem", back_populates="cart")
    user = relationship("User", back_populates="carts")


class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    stock = Column(Integer)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    last_modified = Column(DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now())


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    country = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False, index=True)
    address = Column(String, index=True, nullable=False)

    user = relationship("User", back_populates="addresses")
