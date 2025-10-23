import base64
from typing import Any

import httpx

from src.core.config import get_settings
from src.core.exceptions import APIClientError
from src.core.interfaces import IAPIClient
from src.core.logging import get_logger

logger = get_logger(__name__)


class SferaAPIClient(IAPIClient):
    BASE_PATH = "/app/sourcecode/api/api/v2"

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.sfera_api_url
        self.timeout = self.settings.sfera_api_timeout

        credentials = f"{self.settings.sfera_api_username}:{self.settings.sfera_api_password}"
        credentials_base64 = base64.b64encode(credentials.encode()).decode()

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {credentials_base64}",
        }

        logger.info(f"API Client initialized for {self.base_url}")

    async def authenticate(self) -> None:
        logger.debug("Using Basic Authentication")

    async def get(self, endpoint: str, **params: Any) -> dict[str, Any]:
        url = f"{self.base_url}{self.BASE_PATH}/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                logger.debug(f"GET {url}")
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP {e.response.status_code}: {e.response.text}")
            raise APIClientError(
                f"HTTP error {e.response.status_code}",
                details={"url": url, "response": e.response.text},
            )
        except httpx.RequestError as e:
            logger.error(f"Request failed: {str(e)}")
            raise APIClientError(f"Request failed: {str(e)}", details={"url": url})
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise APIClientError(f"Unexpected error: {str(e)}", details={"url": url})

    async def post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{self.BASE_PATH}/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                logger.debug(f"POST {url}")
                response = await client.post(url, headers=self.headers, json=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP {e.response.status_code}: {e.response.text}")
            raise APIClientError(
                f"HTTP error {e.response.status_code}",
                details={"url": url, "response": e.response.text},
            )
        except httpx.RequestError as e:
            logger.error(f"Request failed: {str(e)}")
            raise APIClientError(f"Request failed: {str(e)}", details={"url": url})
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise APIClientError(f"Unexpected error: {str(e)}", details={"url": url})
