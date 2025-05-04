from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user

from database import get_db
from schemas import AddressUpdate, AddressCreate, AddressOut
import crud
from models import User
from utils.dependencies import get_current_user

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("/add", response_model=AddressOut)
async def create_address(current_user: User = Depends(get_current_user),
                         address: AddressCreate = Depends(AddressCreate), db: AsyncSession = Depends(get_db)):
    if not current_user.is_admin or address.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = crud.get_user_by_id(db,address.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    added_address = await crud.create_address(db, address)
    return added_address


@router.put("/update", response_model=AddressOut)
async def update_address(new_address: AddressUpdate, address_id: int, current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    old_address = await crud.get_address(db, address_id)
    if old_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    if old_address.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    updated_address = await crud.update_address(db, new_address, address_id)
    return updated_address


@router.delete("/delete", response_model=AddressOut)
async def delete_address(address_id: int, current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    address = await crud.get_address(db, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    if address.user_id != current_user.id or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await crud.delete_address(db, address_id)

@router.get("/{address_id}", response_model=AddressOut)
async def get_address(address_id: int, db: AsyncSession = Depends(get_db)):
    address = await crud.get_address(db, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return address
