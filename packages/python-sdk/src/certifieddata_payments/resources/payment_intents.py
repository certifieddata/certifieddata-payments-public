"""Payment intents resource."""

from typing import Any, Optional
from .._http import HttpClient


class PaymentIntentsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        amount: int,
        currency: str,
        rail: str,
        customer_id: Optional[str] = None,
        payee_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            "/v1/payment-intents",
            json={
                "amount": amount,
                "currency": currency,
                "rail": rail,
                "customer_id": customer_id,
                "payee_id": payee_id,
                "description": description,
                "metadata": metadata,
            },
            idempotency_key=idempotency_key,
        )

    def get(self, payment_intent_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/v1/payment-intents/{payment_intent_id}")

    def list(
        self,
        *,
        limit: Optional[int] = None,
        starting_after: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            "/v1/payment-intents",
            params={"limit": limit, "starting_after": starting_after},
        )

    def confirm(
        self,
        payment_intent_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            f"/v1/payment-intents/{payment_intent_id}/confirm",
            idempotency_key=idempotency_key,
        )

    def cancel(
        self,
        payment_intent_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            f"/v1/payment-intents/{payment_intent_id}/cancel",
            idempotency_key=idempotency_key,
        )
