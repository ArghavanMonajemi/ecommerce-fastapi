from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User, Product, Cart, CartItem, Address
from schemas import UserCreate, UserUpdate, ProductCreate, ProductUpdate, CartCreate, CartUpdate, CartItemCreate, \
    CartItemUpdate, AddressCreate, AddressUpdate
from fastapi import HTTPException
import utils.security as security
from typing import List, Type, Any
from sqlalchemy.sql import Select
from sqlalchemy.orm import DeclarativeMeta
from utils.enums import CartStatus


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate):
    try:
        hashed_password = security.hash_password(user.password)
        db_user = User(username=user.username, email=user.email, password=hashed_password, first_name=user.first_name,
                       last_name=user.last_name, is_admin=user.is_admin)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add the user. ERROR:" + str(e))


async def update_user(db: AsyncSession, user_update: UserUpdate, user_id: int):
    try:
        user = await get_user_by_id(db, user_id)
        if user is None:
            return False
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            hashed_password = security.hash_password(update_data["password"])
            update_data["password"] = hashed_password
        for key, value in update_data.items():
            setattr(user, key, value)

        user.last_modified = datetime.now()

        await db.commit()
        await db.refresh(user)
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update the user. ERROR:" + str(e))


async def delete_user(db: AsyncSession, user_id: int):
    try:
        user = await get_user_by_id(db, user_id)
        if user is not None:
            return False

        await db.delete(user)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete the user. ERROR:" + str(e))


async def create_product(db: AsyncSession, product: ProductCreate):
    try:
        db_product = Product(name=product.name, price=product.price, description=product.description,
                             stock=product.stock, image_url=product.image_url)
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        return db_product
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create the product. ERROR:" + str(e))


async def get_product_by_id(db: AsyncSession, product_id: int):
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalars().first()


async def get_all_product(db: AsyncSession):
    result = await db.execute(select(Product))
    return result.scalars().all


async def get_all_product_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Product).where(Product.name == name))
    return result.scalars().all()


async def update_product(db: AsyncSession, product_update: ProductUpdate, product_id: int):
    try:
        product = await get_product_by_id(db, product_id)
        if product is None:
            return False
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        product.last_modified = datetime.now()

        await db.commit()
        await db.refresh(product)
        return True

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update the product. ERROR:" + str(e))


async def delete_product(db: AsyncSession, product_id: int):
    try:
        product = await get_product_by_id(db, product_id)
        if product is None:
            return False
        await db.delete(product)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete the product. ERROR:" + str(e))


async def get_cart_item(db: AsyncSession, cart_item_id: int):
    cart_item = await db.execute(select(CartItem).where(CartItem.id == cart_item_id))
    return cart_item.scalars().first()


async def get_cart_cart_items(db: AsyncSession, cart_id: int):
    items = await db.execute(select(CartItem).where(CartItem.cart_id == cart_id))
    return items.scalars().all()


async def update_cart_item(db: AsyncSession, cart_item_update: CartItemUpdate, cart_item_id: int):
    try:
        item = await get_cart_item(db, cart_item_id)
        if item is None:
            return False
        update_data = cart_item_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update the cart item. ERROR:" + str(e))


async def create_cart_item(db: AsyncSession, item: CartItemCreate):
    try:
        items = await get_cart_cart_items(db, item.cart_id)
        for i in items:
            if i.product_id == item.product_id:
                update_item = CartItemUpdate(quantity=i.quantity + item.quantity)
                return await update_cart_item(db, update_item, i.id)
        db_item = CartItem(cart_id=item.cart_id, product_id=item.product_id, quantity=item.quantity)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create the cart item. ERROR:" + str(e))


async def delete_cart_item(db: AsyncSession, cart_item_id: int):
    try:
        item = await get_cart_item(db, cart_item_id)
        if item is None:
            return False
        await db.delete(item)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete the cart item. ERROR:" + str(e))


async def create_cart(db: AsyncSession, cart: CartCreate):
    try:
        open_cart = await select_with_filter(db, Cart, Cart.status == CartStatus.OPEN, Cart.user_id == cart.user_id)
        if open_cart is None:
            db_cart = Cart(user_id=cart.user_id, status=cart.status)
            db.add(db_cart)
            await db.commit()
            await db.refresh(db_cart)
            return db_cart
        else:
            return open_cart
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create the cart. ERROR:" + str(e))


async def get_cart(db: AsyncSession, cart_id: int):
    cart = await db.execute(select(Cart).where(Cart.id == cart_id))
    return cart.scalars().first()


async def get_user_carts(db: AsyncSession, user_id: int):
    carts = await db.execute(select(Cart).where(Cart.user_id == user_id))
    return carts.scalars().all()


async def update_cart(db: AsyncSession, cart_update: CartUpdate, cart_id: int):
    try:
        cart = await get_cart(db, cart_id)
        if cart is None:
            return False
        update_data = cart_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(cart, key, value)
        await db.commit()
        await db.refresh(cart)
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update the cart. ERROR:" + str(e))


async def delete_cart(db: AsyncSession, cart_id: int):
    try:
        cart = await get_cart(db, cart_id)
        if cart is None:
            return False
        await db.delete(cart)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete the cart. ERROR:" + str(e))


async def create_address(db: AsyncSession, address: AddressCreate):
    if get_user_by_id(db, address.user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        db_address = Address(user_id=address.user_id, country=address.country, city=address.city,
                             address=address.address)
        db.add(db_address)
        await db.commit()
        await db.refresh(db_address)
        return db_address
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create the address. ERROR:" + str(e))


async def get_address(db: AsyncSession, address_id: int):
    result = await db.execute(select(Address).where(Address.id == address_id))
    return result.scalars().first()


async def get_user_all_address(db: AsyncSession, user_id: int):
    result = await db.execute(select(Address).where(Address.user_id == user_id))
    return result.scalars().all()


async def update_address(db: AsyncSession, address_update: AddressUpdate, address_id: int):
    address = await get_address(db, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    try:
        update_data = address_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(address, key, value)
        await db.commit()
        await db.refresh(address)
        return address
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update the address. ERROR:" + str(e))


async def delete_address(db: AsyncSession, address_id: int):
    try:
        address = await get_address(db, address_id)
        if address is None:
            return False
        await db.delete(address)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete the address. ERROR:" + str(e))


async def select_with_filter(
        db: AsyncSession,
        model: Type[DeclarativeMeta],
        *filters,
        order_by: Any = None
) -> List[Any]:
    stmt: Select = select(model).where(*filters)
    if order_by:
        stmt = stmt.order_by(order_by)

    result = await db.execute(stmt)
    return result.scalars().all()
