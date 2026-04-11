"""CertifiedData Agent Commerce Python SDK — main client."""

import os
from typing import Optional

from ._http import HttpClient
from .resources.payees import PayeesResource
from .resources.payment_intents import PaymentIntentsResource
from .resources.transactions import TransactionsResource
from .resources.settlements import SettlementsResource
from .resources.refunds import RefundsResource
from .resources.events import EventsResource
from .webhooks import verify_webhook_signature as _verify_webhook_signature


class CertifiedDataAgentCommerceClient:
    """
    CertifiedData Agent Commerce API client.

    Usage::

        from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient

        # api_key reads CDAC_API_KEY, base_url reads CDAC_BASE_URL
        client = CertifiedDataAgentCommerceClient()

        # or pass explicitly:
        client = CertifiedDataAgentCommerceClient(
            api_key="cdp_test_...",
            base_url="https://certifieddata.io",
        )

    Use ``cdp_test_`` keys for test mode, ``cdp_live_`` keys for production.
    Both key types route to the same base URL — the prefix controls the environment.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        api_version: str = "2025-01-01",
        timeout: float = 30.0,
    ) -> None:
        resolved_key = api_key or os.environ.get("CDAC_API_KEY")
        if not resolved_key:
            raise ValueError("api_key is required. Pass it directly or set CDAC_API_KEY.")
        resolved_url = base_url or os.environ.get("CDAC_BASE_URL") or "https://certifieddata.io"
        self._http = HttpClient(
            api_key=resolved_key,
            base_url=resolved_url,
            api_version=api_version,
            timeout=timeout,
        )
        self.payees = PayeesResource(self._http)
        self.payment_intents = PaymentIntentsResource(self._http)
        self.transactions = TransactionsResource(self._http)
        self.settlements = SettlementsResource(self._http)
        self.refunds = RefundsResource(self._http)
        self.events = EventsResource(self._http)

    def verify_webhook_signature(
        self,
        raw_body: str | bytes,
        signature_header: str,
        timestamp_header: str,
        secret: str,
        tolerance_seconds: int = 300,
    ) -> bool:
        """
        Verify a CDP webhook signature.

        :param raw_body: Raw request body before any JSON parsing.
        :param signature_header: ``CDAC-Signature`` header value.
        :param timestamp_header: ``CDAC-Timestamp`` header value.
        :param secret: Webhook endpoint secret.
        :param tolerance_seconds: Timestamp tolerance in seconds (default 300).
        """
        return _verify_webhook_signature(
            raw_body, signature_header, timestamp_header, secret, tolerance_seconds
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> "CertifiedDataAgentCommerceClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
