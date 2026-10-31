import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "fastapi_1")
    POSTGRES_HOST=os.getenv("POSTGRES_HOST", "127.0.0.1")
    POSTGRES_PORT=os.getenv("POSTGRES_PORT", "5431")

    POSTGRES_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    TOKEN_TTL = 60 * 60 * 48

config = Config()