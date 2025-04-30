from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import CartItemCreate, CartItemUpdate, CartItemOut, CartUpdate
import crud

router = APIRouter(prefix="/cart_items", tags=["CartItem"])


@router.get("/{cart_item_id}", response_model=CartItemOut)
async def get_cart_item(cart_item_id: int, db: AsyncSession = Depends(get_db)):
    cart_item = await crud.get_cart_item(db, cart_item_id)
    if cart_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return cart_item


@router.post("/add", response_model=CartItemOut)
async def add_cart_item(cart_item: CartItemCreate, db: AsyncSession = Depends(get_db)):
    item = await crud.create_cart_item(db, cart_item)
    if item is None:
        raise HTTPException(status_code=500, detail="Failed to create the cart item.")
    cart = await crud.get_cart(db, item.cart_id)
    price = 0
    for item in cart.items:
        price += item.price
    new_cart = CartUpdate(total_price=price)
    await crud.update_cart(db, new_cart, cart.id)
    return item


@router.put("/{cart_item_id}", response_model=CartItemOut)
async def update_cart_item(cart_item: CartItemUpdate, cart_item_id: int, db: AsyncSession = Depends(get_db)):
    item = await crud.get_cart_item(db, cart_item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = await crud.update_cart_item(db, cart_item, cart_item_id)
    if updated_item is None:
        raise HTTPException(status_code=500, detail="Failed to update the cart item.")
    cart = await crud.get_cart(db, item.cart_id)
    price = 0
    for item in cart.items:
        price += item.price
    new_cart = CartUpdate(total_price=price)
    await crud.update_cart(db, new_cart, cart.id)
    return updated_item


@router.delete("/{cart_item_id}", response_model=CartItemOut)
async def delete_cart_item(cart_item_id: int, db: AsyncSession = Depends(get_db)):
    item = await crud.get_cart_item(db, cart_item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    is_delete = await crud.delete_cart_item(db, cart_item_id)
    if is_delete is None:
        raise HTTPException(status_code=500, detail="Failed to delete the cart item.")
    return item


@router.get("/{cart_id}", response_model=List[CartItemOut])
async def get_cart_items(cart_id: int, db: AsyncSession = Depends(get_db)):
    cart = await crud.get_cart(db, cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="cart not found")
    return await crud.get_cart_cart_items(db, cart_id)
