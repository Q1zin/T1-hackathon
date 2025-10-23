from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.core.config import get_settings
from src.core.logging import get_logger, setup_logging

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    try:
        from src.storage.database import engine
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established")
        yield
        await engine.dispose()
        logger.info("Database engine disposed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

allowed_origins = (
    ["*"] if settings.debug
    else ["http://localhost:3000", "http://localhost:8000"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, Any]:
    from src.storage.database import engine

    db_status = "unknown"
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Health check failed: {e}")

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "version": settings.app_version,
        "database": db_status,
    }


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "data_collection": f"{settings.api_prefix}/data",
            "tasks": f"{settings.api_prefix}/tasks",
        },
    }


from src.api.routes import data_collection, tasks

app.include_router(
    data_collection.router,
    prefix=f"{settings.api_prefix}/data",
    tags=["Data Collection"],
)

app.include_router(
    tasks.router,
    prefix=settings.api_prefix,
    tags=["Tasks"],
)
