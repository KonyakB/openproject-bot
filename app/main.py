from fastapi import FastAPI

from app.api.admin import router as admin_router
from app.api.discord import router as discord_router
from app.api.health import router as health_router
from app.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(discord_router)
    app.include_router(admin_router)
    return app


app = create_app()
