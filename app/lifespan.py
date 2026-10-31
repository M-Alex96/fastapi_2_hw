from contextlib import asynccontextmanager
from fastapi import FastAPI
from db import engine, Base, AsyncSessionLocal
import models
from sqlalchemy import select


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        for role_name in ("user", "admin"):
            if not await session.scalar(select(models.Role).where(models.Role.name == role_name)):
                session.add(models.Role(name=role_name))
        await session.commit()
    yield
    await engine.dispose()