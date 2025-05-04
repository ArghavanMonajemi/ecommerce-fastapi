from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from utils.dependencies import get_current_user
from database import get_db
from schemas import UserCreate, UserOut, UserUpdate
import crud
from utils.security import verify_password
from utils.jwt import create_access_token
from models import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    user = await crud.create_user(db, user_data)
    return user


@router.post("/login")
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await crud.get_user_by_username(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_name}")
async def get_user_by_username(user_name: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_username(db, user_name)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/by_email/")
async def get_user_by_email(user_email: str, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_email(db, user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/addresses")
async def get_user_addresses(user_id: int,db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = await crud.get_user_by_id(db, user_id)
    if not current_user.is_admin or current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    addresses = await crud.get_user_addresses(db, user_id)
    return addresses


@router.put("/{user_id}")
async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.update_user(db, user_data, user_id)


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.delete_user(db, user)
