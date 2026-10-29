from fastapi import FastAPI, Depends, HTTPException, status
import schemas
from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from lifespan import lifespan
from sqlalchemy import select
import models
from dependencies import get_db_session
from services import add_item, get_item, update_item, delete_item
from auth import check_password, get_current_user

app = FastAPI(
    title="Сервис объявлений купли/продажи",
    description="Домашнее задание к лекции «Создание REST API на FastApi» часть 2",
    version="2.0.1",
    lifespan=lifespan,
)

sessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def is_admin(user: models.User) -> bool:
    return any(r.name == "admin" for r in user.roles)


@app.post("/login", response_model=schemas.LoginResponse, summary="Авторизация")
async def login(login_data: schemas.LoginRequest, session: sessionDependency):
    user = await session.scalar(select(models.User).where(models.User.name == login_data.name))
    if user is None or not check_password(login_data.password, user.password):
        raise HTTPException(401, "Incorrect username or password")
    new_token = models.Token(user_id=user.id)
    session.add(new_token)
    await session.commit()
    await session.refresh(new_token)
    return schemas.LoginResponse(id=new_token.id, token=new_token.token)


@app.post("/user", response_model=schemas.CreateUserResponse, summary="Создать нового пользователя")
async def create_user(user_data: schemas.CreateUserRequest, session: sessionDependency):
    new_user = await add_item(session, models.User, user_data)
    role = await session.scalar(select(models.Role).where(models.Role.name == "user"))
    if role:
        new_user.roles.append(role)
        await session.commit()
    return schemas.CreateUserResponse(id=new_user.id)


@app.post("/advertisement", response_model=schemas.CreateAdvertisementResponse, summary="Создать новое объявление")
async def create_advertisement(
    adv_data: schemas.CreateAdvertisementRequest,
    session: sessionDependency,
    current_user: Optional[models.User] = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(403, "Not enough permissions")
    new_adv = await add_item(session, models.Advertisement, adv_data)
    return schemas.CreateAdvertisementResponse(id=new_adv.id)


@app.get("/user/{item_id}", response_model=schemas.GetUsersResponse, summary="Получить пользователя по id")
async def get_user(item_id: int, session: sessionDependency):
    user = await get_item(session, models.User, item_id)
    return schemas.GetUsersResponse(**user.user_dict())


@app.get("/advertisement/{item_id}", response_model=schemas.GetAdvertisementsResponse, summary="Получить объявление по id")
async def get_advertisement(item_id: int, session: sessionDependency):
    adv = await get_item(session, models.Advertisement, item_id)
    return schemas.GetAdvertisementsResponse(**adv.advertisement_dict())


@app.get("/advertisement", response_model=list[schemas.GetAdvertisementsResponse], summary="Поиск объявлений по полям")
async def get_advertisements_by_fields(
    session: sessionDependency,
    title: Optional[str] = None,
    description: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    author_id: Optional[int] = None,
):
    stmt = select(models.Advertisement)
    if title:
        stmt = stmt.where(models.Advertisement.title.ilike(f"%{title}%"))
    if description:
        stmt = stmt.where(models.Advertisement.description.ilike(f"%{description}%"))
    if price_min is not None:
        stmt = stmt.where(models.Advertisement.price >= price_min)
    if price_max is not None:
        stmt = stmt.where(models.Advertisement.price <= price_max)
    if author_id is not None:
        stmt = stmt.where(models.Advertisement.author_id == author_id)
    result = await session.execute(stmt)
    advs = result.scalars().all()
    return [schemas.GetAdvertisementsResponse(**a.advertisement_dict()) for a in advs]


@app.patch("/user/{item_id}", response_model=schemas.UpdateUserResponse, summary="Обновить пользователя")
async def update_user(
    item_id: int,
    update_data: schemas.UpdateUserRequest,
    session: sessionDependency,
    current_user: Optional[models.User] = Depends(get_current_user),
):
    if current_user is None or (current_user.id != item_id and not is_admin(current_user)):
        raise HTTPException(403, "Not enough permissions")
    updated_user = await update_item(session, models.User, item_id, update_data)
    return schemas.UpdateUserResponse(**updated_user.user_dict())


@app.patch("/advertisement/{item_id}", response_model=schemas.UpdateAdvertisementResponse, summary="Обновить объявление")
async def update_advertisement(
    item_id: int,
    update_data: schemas.UpdateAdvertisementRequest,
    session: sessionDependency,
    current_user: Optional[models.User] = Depends(get_current_user),
):
    adv = await get_item(session, models.Advertisement, item_id)
    if current_user is None or (current_user.id != adv.author_id and not is_admin(current_user)):
        raise HTTPException(403, "Not enough permissions")
    updated_adv = await update_item(session, models.Advertisement, item_id, update_data)
    return schemas.UpdateAdvertisementResponse(**updated_adv.advertisement_dict())


@app.delete("/user/{item_id}", response_model=schemas.DeleteUserResponse, summary="Удалить пользователя")
async def delete_user(
    item_id: int,
    session: sessionDependency,
    current_user: Optional[models.User] = Depends(get_current_user),
):
    if current_user is None or (current_user.id != item_id and not is_admin(current_user)):
        raise HTTPException(403, "Not enough permissions")
    await delete_item(session, models.User, item_id)
    return schemas.DeleteUserResponse()


@app.delete("/advertisement/{item_id}", response_model=schemas.DeleteAdvertisementResponse, summary="Удалить объявление")
async def delete_advertisement(
    item_id: int,
    session: sessionDependency,
    current_user: Optional[models.User] = Depends(get_current_user),
):
    adv = await get_item(session, models.Advertisement, item_id)
    if current_user is None or (current_user.id != adv.author_id and not is_admin(current_user)):
        raise HTTPException(403, "Not enough permissions")
    await delete_item(session, models.Advertisement, item_id)
    return schemas.DeleteAdvertisementResponse()