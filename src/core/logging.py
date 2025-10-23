"""Настройка логирования."""

import sys
from typing import Any

from loguru import logger

from src.core.config import get_settings


def setup_logging() -> None:
    """Настройка логирования приложения."""
    settings = get_settings()

    # Удаляем стандартный обработчик
    logger.remove()

    # Формат логов
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    if settings.log_format == "json":
        # JSON формат для production
        logger.add(
            sys.stdout,
            format="{message}",
            level=settings.log_level,
            serialize=True,
        )
    else:
        # Читаемый формат для development
        logger.add(
            sys.stdout,
            format=log_format,
            level=settings.log_level,
            colorize=True,
        )

    # Файл для ошибок
    logger.add(
        "logs/errors.log",
        format=log_format,
        level="ERROR",
        rotation="1 week",
        retention="1 month",
        compression="zip",
    )

    # Файл для всех логов
    logger.add(
        "logs/app.log",
        format=log_format,
        level="INFO",
        rotation="1 day",
        retention="1 week",
        compression="zip",
    )


def get_logger(name: str) -> Any:
    """Получение логгера с именем модуля."""
    return logger.bind(name=name)
