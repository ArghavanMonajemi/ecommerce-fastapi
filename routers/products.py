from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import ProductCreate, ProductUpdate, ProductOut
import crud
from utils.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/add", response_model=ProductOut)
async def add_product(product_data: ProductCreate, db: AsyncSession = Depends(get_db),
                      current_user=Depends(get_current_user)):
    if crud.get_all_product_by_name(db, product_data.name) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="a product with this name already exist"
        )
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can perform this action")
    product = crud.create_product(db, product_data)
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, product_data: ProductUpdate, db: AsyncSession = Depends(get_db),
                         current_user=Depends(get_current_user)):
    product = await crud.get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can perform this action")
    return crud.update_product(db, product_data, product_id)


@router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    product = await crud.get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can perform this action")
    return crud.delete_product(db, product_id)


@router.get("/{product_id}")
async def get_product_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await crud.get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/", response_model=list[ProductOut])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    products = crud.get_all_product(db)
    return products


@router.get("/{product_name}", response_model=ProductOut)
async def get_product_by_name(product_name: str, db: AsyncSession = Depends(get_db)):
    product = crud.get_all_product_by_name(db, product_name)
    return product
