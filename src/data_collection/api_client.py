"""HTTP клиент для работы с T1 Сфера.Код API."""

import base64
from typing import Any

import httpx

from src.core.config import get_settings
from src.core.exceptions import APIClientError
from src.core.interfaces import IAPIClient
from src.core.logging import get_logger

logger = get_logger(__name__)


class SferaAPIClient(IAPIClient):
    """Клиент для работы с T1 Сфера.Код API."""

    def __init__(self) -> None:
        """Инициализация клиента."""
        self.settings = get_settings()
        self.base_url = self.settings.sfera_api_url
        self.timeout = self.settings.sfera_api_timeout

        # Формируем Basic Auth заголовок
        credentials = f"{self.settings.sfera_api_username}:{self.settings.sfera_api_password}"
        credentials_base64 = base64.b64encode(credentials.encode()).decode()

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {credentials_base64}",
        }

        logger.info(f"API Client initialized for {self.base_url}")

    async def authenticate(self) -> None:
        """
        Аутентификация не требуется - используется Basic Auth.

        Метод оставлен для совместимости с интерфейсом.
        """
        # Basic Auth не требует отдельной аутентификации
        logger.info("Using Basic Authentication")

    async def get(self, endpoint: str, **params: Any) -> dict[str, Any]:
        """
        Выполнить GET запрос.

        Args:
            endpoint: Путь к эндпоинту
            **params: Query параметры

        Returns:
            Ответ от API

        Raises:
            APIClientError: При ошибке запроса
        """
        # Базовый путь для Source Code API v2
        base_path = "/app/sourcecode/api/api/v2"
        url = f"{self.base_url}{base_path}/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                logger.info(f"GET request to {url} with params: {params}")
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise APIClientError(
                f"HTTP error {e.response.status_code}",
                details={"url": url, "response": e.response.text},
            )
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise APIClientError(f"Request failed: {str(e)}", details={"url": url})
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise APIClientError(f"Unexpected error: {str(e)}", details={"url": url})

    async def post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Выполнить POST запрос.

        Args:
            endpoint: Путь к эндпоинту
            data: Данные для отправки

        Returns:
            Ответ от API

        Raises:
            APIClientError: При ошибке запроса
        """
        base_path = "/app/sourcecode/api/api/v2"
        url = f"{self.base_url}{base_path}/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                logger.info(f"POST request to {url}")
                response = await client.post(url, headers=self.headers, json=data)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise APIClientError(
                f"HTTP error {e.response.status_code}",
                details={"url": url, "response": e.response.text},
            )
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise APIClientError(f"Request failed: {str(e)}", details={"url": url})
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise APIClientError(f"Unexpected error: {str(e)}", details={"url": url})
