"""Payees resource."""

from typing import Any, Optional
from .._http import HttpClient


class PayeesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        entity_type: str,
        legal_name: Optional[str] = None,
        email: Optional[str] = None,
        default_payout_method: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            "/v1/payees",
            json={
                "entity_type": entity_type,
                "legal_name": legal_name,
                "email": email,
                "default_payout_method": default_payout_method,
                "metadata": metadata,
            },
            idempotency_key=idempotency_key,
        )

    def get(self, payee_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/v1/payees/{payee_id}")

    def list(
        self,
        *,
        limit: Optional[int] = None,
        starting_after: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            "/v1/payees",
            params={"limit": limit, "starting_after": starting_after},
        )

    def update(
        self,
        payee_id: str,
        *,
        legal_name: Optional[str] = None,
        email: Optional[str] = None,
        default_payout_method: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        body = {}
        if legal_name is not None:
            body["legal_name"] = legal_name
        if email is not None:
            body["email"] = email
        if default_payout_method is not None:
            body["default_payout_method"] = default_payout_method
        if metadata is not None:
            body["metadata"] = metadata
        return self._http.request(
            "PATCH",
            f"/v1/payees/{payee_id}",
            json=body,
            idempotency_key=idempotency_key,
        )

    def create_alias(
        self,
        payee_id: str,
        *,
        external_system: str,
        external_ref: str,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            f"/v1/payees/{payee_id}/aliases",
            json={"external_system": external_system, "external_ref": external_ref},
            idempotency_key=idempotency_key,
        )

    def list_aliases(
        self,
        payee_id: str,
        *,
        limit: Optional[int] = None,
        starting_after: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            f"/v1/payees/{payee_id}/aliases",
            params={"limit": limit, "starting_after": starting_after},
        )

    def create_payout_destination(
        self,
        payee_id: str,
        *,
        rail_type: str,
        is_default: bool = False,
        processor_ref: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "POST",
            f"/v1/payees/{payee_id}/payout-destinations",
            json={
                "rail_type": rail_type,
                "is_default": is_default,
                "processor_ref": processor_ref,
                "metadata": metadata,
            },
            idempotency_key=idempotency_key,
        )

    def list_payout_destinations(
        self,
        payee_id: str,
        *,
        limit: Optional[int] = None,
        starting_after: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._http.request(
            "GET",
            f"/v1/payees/{payee_id}/payout-destinations",
            params={"limit": limit, "starting_after": starting_after},
        )
