"""Transactions resource."""

from typing import Any, Optional
from .._http import HttpClient


class TransactionsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        amount: int,
        currency: str,
        rail: str,
        payment_intent_id: Optional[str] = None,
        payee_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            "/v1/transactions",
            json={
                "amount": amount,
                "currency": currency,
                "rail": rail,
                "payment_intent_id": payment_intent_id,
                "payee_id": payee_id,
                "customer_id": customer_id,
                "description": description,
                "metadata": metadata,
            },
            idempotency_key=idempotency_key,
        )

    def get(self, transaction_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/v1/transactions/{transaction_id}")

    def list(
        self,
        *,
        limit: Optional[int] = None,
        starting_after: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            "/v1/transactions",
            params={"limit": limit, "starting_after": starting_after},
        )

    def attach_links(
        self,
        transaction_id: str,
        *,
        artifact_id: Optional[str] = None,
        certificate_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        model_id: Optional[str] = None,
        output_id: Optional[str] = None,
        receipt_hash: Optional[str] = None,
        external_reference: Optional[str] = None,
        provenance_metadata: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            f"/v1/transactions/{transaction_id}/attach-links",
            json={
                "artifact_id": artifact_id,
                "certificate_id": certificate_id,
                "decision_id": decision_id,
                "dataset_id": dataset_id,
                "model_id": model_id,
                "output_id": output_id,
                "receipt_hash": receipt_hash,
                "external_reference": external_reference,
                "provenance_metadata": provenance_metadata,
            },
            idempotency_key=idempotency_key,
        )

    def capture(
        self,
        transaction_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            f"/v1/transactions/{transaction_id}/capture",
            idempotency_key=idempotency_key,
        )

    def cancel(
        self,
        transaction_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            f"/v1/transactions/{transaction_id}/cancel",
            idempotency_key=idempotency_key,
        )
