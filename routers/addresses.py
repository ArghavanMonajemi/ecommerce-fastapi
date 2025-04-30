from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import AddressUpdate, AddressCreate, AddressOut
import crud
from models import User
from utils.dependencies import get_current_user

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.post("/add", response_model=AddressOut, status_code=201)
async def create_address(current_user: User = Depends(get_current_user),
                         address: AddressCreate = Depends(AddressCreate), db: AsyncSession = Depends(get_db)):
    if address.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    added_address = await crud.create_address(db, address)
    return added_address


@router.put("/update", response_model=AddressOut, status_code=204)
async def update_address(new_address: AddressUpdate, address_id: int, current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    old_address = await crud.get_address(db, address_id)
    if old_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    if old_address.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    updated_address = await crud.update_address(db, new_address, address_id)
    return updated_address


@router.delete("/delete", response_model=AddressOut, status_code=204)
async def delete_address(address_id: int, current_user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    address = await crud.get_address(db, address_id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    if address.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    await crud.delete_address(db, address_id)
