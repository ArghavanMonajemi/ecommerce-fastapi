import asyncio
from database import engine, Base
from routers import users, addresses, carts, cart_items, products
from fastapi import FastAPI
import uvicorn

app = FastAPI()

app.include_router(users.router)
app.include_router(addresses.router)
app.include_router(carts.router)
app.include_router(cart_items.router)
app.include_router(products.router)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


#if __name__ == "__main__":
#    asyncio.run(init_models())

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
