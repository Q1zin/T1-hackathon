"""Основной модуль FastAPI приложения."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.logging import get_logger, setup_logging

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle менеджер приложения."""
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Попытка инициализации БД (опционально)
    try:
        from src.storage.database import engine
        logger.info("Database engine initialized")
        yield
        # Shutdown
        await engine.dispose()
        logger.info("Database engine disposed")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}. Running without database.")
        yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Настроить для production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Проверка здоровья приложения."""
    return {"status": "ok", "version": settings.app_version}


@app.get("/")
async def root() -> dict[str, Any]:
    """Корневой эндпоинт."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "data_collection": f"{settings.api_prefix}/data",
        },
    }


# Подключаем роутеры
from src.api.routes import data_collection

app.include_router(
    data_collection.router,
    prefix=f"{settings.api_prefix}/data",
    tags=["Data Collection"],
)
