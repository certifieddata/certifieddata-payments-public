"""Internal HTTP client wrapper using httpx."""

from typing import Any, Optional
import httpx
from .errors import _raise_for_status


class HttpClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.certifieddata.io",
        api_version: str = "2025-01-01",
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "CDP-API-Version": api_version,
                "Content-Type": "application/json",
                "User-Agent": "certifieddata-payments-python/0.1.0",
            },
            timeout=timeout,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[Any] = None,
        idempotency_key: Optional[str] = None,
    ) -> Any:
        headers: dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        # Remove None values from query params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = self._client.request(
            method,
            path,
            params=params or None,
            json=json,
            headers=headers,
        )

        body: Any = None
        if response.content:
            try:
                body = response.json()
            except Exception:
                body = {"raw": response.text}

        if not response.is_success:
            _raise_for_status(response.status_code, body)

        return body

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
