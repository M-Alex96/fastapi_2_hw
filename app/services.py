from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar
from pydantic import BaseModel as PydanticBaseModel
from db import Base
from auth import hash_password

ModelT = TypeVar("ModelT", bound=Base)
SchemaT = TypeVar("SchemaT", bound=PydanticBaseModel)

async def add_item(
        session: AsyncSession,
        orm_model: type[ModelT],
        item_data: SchemaT
) -> ModelT:
    data = item_data.model_dump()
    if data.get("password"):
        data["password"] = hash_password(data["password"])
    new_item = orm_model(**data)
    session.add(new_item)
    try:
        await session.commit()
        await session.refresh(new_item)
        return new_item
    except IntegrityError as e:
        await session.rollback()
        if isinstance(e.orig, UniqueViolationError) and e.orig.pgcode == '23505':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with such data already exists."
            )
        else:
            raise e


async def get_item(
        session: AsyncSession,
        orm_model: type[ModelT],
        item_id: int
) -> ModelT:
    stmt = select(orm_model).where(orm_model.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{orm_model.__name__} with id {item_id} not found"
        )
    return item


async def update_item(
        session: AsyncSession,
        orm_model: type[ModelT],
        item_id: int,
        update_data: SchemaT
) -> ModelT:
    item = await get_item(session, orm_model, item_id)

    update_dict = update_data.model_dump(exclude_unset=True)
    if update_dict.get("password"):
        update_dict["password"] = hash_password(update_dict["password"])

    for key, value in update_dict.items():
        setattr(item, key, value)

    try:
        await session.commit()
        await session.refresh(item)
        return item
    except IntegrityError as e:
        await session.rollback()
        if isinstance(e.orig, UniqueViolationError):
            raise HTTPException(status.HTTP_409_CONFLICT, detail="")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="")

async def delete_item(
        session: AsyncSession,
        orm_model: type[ModelT],
        item_id: int
) -> None:
    item = await get_item(session, orm_model, item_id)
    await session.delete(item)
    await session.commit()
