"""Сервис кеширования на основе Redis."""

import json
from typing import Any

import redis.asyncio as aioredis

from src.core.config import get_settings
from src.core.interfaces import ICacheService
from src.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RedisCacheService(ICacheService):
    """Сервис кеширования на Redis."""

    def __init__(self) -> None:
        """Инициализация сервиса."""
        self.redis = aioredis.from_url(
            str(settings.redis_url), encoding="utf-8", decode_responses=True
        )
        self.default_ttl = settings.cache_ttl

    async def get(self, key: str) -> Any | None:
        """
        Получить значение из кеша.

        Args:
            key: Ключ

        Returns:
            Значение или None
        """
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Установить значение в кеш.

        Args:
            key: Ключ
            value: Значение
            ttl: Время жизни (секунды)
        """
        try:
            serialized = json.dumps(value)
            await self.redis.set(key, serialized, ex=ttl or self.default_ttl)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")

    async def delete(self, key: str) -> None:
        """
        Удалить значение из кеша.

        Args:
            key: Ключ
        """
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")

    async def clear(self) -> None:
        """Очистить весь кеш."""
        try:
            await self.redis.flushdb()
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")

    async def close(self) -> None:
        """Закрыть соединение."""
        await self.redis.close()
