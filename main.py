import asyncio
from database import engine, Base
import models
from routers import users
from fastapi import FastAPI
import uvicorn

app = FastAPI()

app.include_router(users.router)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
