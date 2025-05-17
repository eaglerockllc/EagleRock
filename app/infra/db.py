from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infra.config import settings

def _dsn()->str:
    return f"postgresql+psycopg://{settings.pg_user}:{settings.pg_password}@{settings.pg_host}:{settings.pg_port}/{settings.pg_db}"

engine = create_engine(_dsn(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
