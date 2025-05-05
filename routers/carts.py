from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import CartCreate, CartUpdate, CartOut, CartItemOut, ProductUpdate
import crud
from models import Cart, User
from utils.enums import CartStatus
from utils.dependencies import get_current_user

router = APIRouter(prefix="/carts", tags=["Cart"])


@router.get("/cart/{cart_id}", response_model=CartOut)
async def get_cart(cart_id: int, db: AsyncSession = Depends(get_db)):
    cart = await crud.get_cart(db, cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@router.get("/user/{user_id}/all", response_model=List[CartOut])
async def get_user_carts(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    carts = await crud.get_user_carts(db, user_id)
    return carts


@router.get("/user/open_cart", response_model=CartOut)
async def get_user_open_cart(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    cart = await crud.get_user_open_cart(db,current_user.id)
    return cart


@router.post("/add_cart", response_model=CartOut)
async def add_cart(cart: CartCreate, db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    open_cart = await get_user_open_cart(current_user, db)
    if open_cart is not None:
        return open_cart
    open_cart = await crud.create_cart(db, cart)
    return open_cart


@router.delete("/{cart_id}", response_model=CartOut)
async def delete_cart(cart_id: int, db: AsyncSession = Depends(get_db)):
    cart = await crud.get_cart(db, cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    cart_items: List[CartItemOut] = await crud.get_cart_cart_items(db, cart_id)
    for item in cart_items:
        await crud.delete_cart_item(db, item.id)
    await crud.delete_cart(db, cart_id)
    return cart


@router.delete("/user/delete/all")
async def delete_user_all_cart(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    carts = await crud.get_user_carts(db, current_user.id)
    for cart in carts:
        await delete_cart(cart.id, db)


@router.put("/{cart_id}", response_model=CartOut)
async def update_cart(cart_id: int, cart: CartUpdate, db: AsyncSession = Depends(get_db)):
    old_cart = await crud.get_cart(db, cart_id)
    if old_cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    updated_cart = await crud.update_cart(db, cart, cart_id)
    return updated_cart


@router.put("/cart/checkout")
async def checkout(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    cart: Cart = await get_user_open_cart(current_user, db)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    price = 0
    for item in cart.items:
        price += item.price
    new_cart = CartUpdate(status=CartStatus.CHECKED_OUT, total_price=price)
    cart = await crud.update_cart(db, new_cart, cart.id)
    if cart is not None:
        for item in cart.items:
            product = await crud.get_product_by_id(db,item.id)
            new_product = ProductUpdate(stock=product.stock - item.stock)
            await crud.update_product(db, new_product, item.id)
    return {"message": "Checkout successful (mocked)"}


@router.put("/cart/cancel")
async def cancel_cart(cart_id: int, db: AsyncSession = Depends(get_db)):
    cart = await crud.get_cart(db, cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    new_cart = CartUpdate(status=CartStatus.CANCELLED)
    await crud.update_cart(db, new_cart, cart_id)
    return {"message": "Cancel successful"}
