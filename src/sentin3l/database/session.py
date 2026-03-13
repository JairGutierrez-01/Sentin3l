from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from sentin3l.config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
