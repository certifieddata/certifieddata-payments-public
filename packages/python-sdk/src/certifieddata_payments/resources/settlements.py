"""Settlements resource."""

from typing import Any, Optional
from .._http import HttpClient


class SettlementsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        payee_id: str,
        amount: int,
        currency: str,
        transaction_ids: list[str],
        destination_id: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            "/v1/settlements",
            json={
                "payee_id": payee_id,
                "amount": amount,
                "currency": currency,
                "transaction_ids": transaction_ids,
                "destination_id": destination_id,
                "metadata": metadata,
            },
            idempotency_key=idempotency_key,
        )

    def get(self, settlement_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/v1/settlements/{settlement_id}")

    def list(
        self,
        *,
        limit: Optional[int] = None,
        starting_after: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            "/v1/settlements",
            params={"limit": limit, "starting_after": starting_after},
        )

    def submit(
        self,
        settlement_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            f"/v1/settlements/{settlement_id}/submit",
            idempotency_key=idempotency_key,
        )

    def cancel(
        self,
        settlement_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            f"/v1/settlements/{settlement_id}/cancel",
            idempotency_key=idempotency_key,
        )
