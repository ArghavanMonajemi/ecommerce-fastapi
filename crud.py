from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User
from schemas import UserCreate, UserUpdate
from fastapi import HTTPException
import utils.security as security

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, id: int):
    result = await db.execute(select(User).where(User.id == id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    try:
        hashed_password = security.hash_password(user.password)
        db_user = User(username=user.username, email=user.email, password=hashed_password, first_name=user.first_name,last_name=user.last_name)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500,detail="Failed to add the user. ERROR:"+str(e))

async def update_user(db: AsyncSession, user_update: UserUpdate, user_id: int):
    try:
        user = get_user_by_id(db, user_id)
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
        raise HTTPException(status_code=500,detail="Failed to update the user. ERROR:"+str(e))

async def delete_user(db: AsyncSession, id: int):
    try:
        user = get_user_by_id(db, id)
        if user is not None:
            return False

        await db.delete(user)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete the user. ERROR:"+str(e))

