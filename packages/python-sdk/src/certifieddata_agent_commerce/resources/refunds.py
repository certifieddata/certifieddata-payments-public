"""Refunds resource."""

from typing import Any, Optional
from .._http import HttpClient


class RefundsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        transaction_id: str,
        amount: int,
        reason: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            "/v1/refunds",
            json={
                "transaction_id": transaction_id,
                "amount": amount,
                "reason": reason,
                "metadata": metadata,
            },
            idempotency_key=idempotency_key,
        )

    def get(self, refund_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/v1/refunds/{refund_id}")

    def list(
        self,
        *,
        limit: Optional[int] = None,
        starting_after: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            "/v1/refunds",
            params={"limit": limit, "starting_after": starting_after},
        )
