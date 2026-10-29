import uuid
import bcrypt
import datetime
from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Token
from config import Config
from sqlalchemy.sql import func
from dependencies import get_db_session
from typing import Optional
from models import User

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

async def check_token(
    token: uuid.UUID = Header(..., alias="x-token"),
    db_session: AsyncSession = Depends(get_db_session)
) -> Token:
    expire_threshold = func.now() - datetime.timedelta(seconds=Config.TOKEN_TTL)

    query = select(Token).where(
        Token.token == token,
        Token.creation_time >= expire_threshold
    )
    token_obj = await db_session.scalar(query)

    if token_obj is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return token_obj

async def get_current_user(
    token: Optional[uuid.UUID] = Header(None, alias="x-token"),
    db_session: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    if token is None:
        return None
    expire = func.now() - datetime.timedelta(seconds=Config.TOKEN_TTL)
    obj = await db_session.scalar(
        select(Token).where(Token.token == token, Token.creation_time >= expire)
    )
    if obj is None:
        raise HTTPException(401, "Invalid or expired token")
    return obj.user