import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.db.base import Base


@pytest.fixture(autouse=True)
def set_test_env() -> None:
    os.environ.setdefault("DISCORD_PUBLIC_KEY", "00")
    os.environ.setdefault("DISCORD_APPLICATION_ID", "app")
    os.environ.setdefault("DISCORD_BOT_TOKEN", "token")
    os.environ.setdefault("OPENPROJECT_BASE_URL", "https://openproject.example.com")
    os.environ.setdefault("OPENPROJECT_API_TOKEN", "op-token")
    os.environ.setdefault("LLM_API_KEY", "llm-token")
    os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    get_settings.cache_clear()


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
