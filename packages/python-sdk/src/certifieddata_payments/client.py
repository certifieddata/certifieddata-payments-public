"""CertifiedData Payments Python SDK — main client."""

from typing import Optional

from ._http import HttpClient
from .resources.payees import PayeesResource
from .resources.payment_intents import PaymentIntentsResource
from .resources.transactions import TransactionsResource
from .resources.settlements import SettlementsResource
from .resources.refunds import RefundsResource
from .resources.events import EventsResource
from .webhooks import verify_webhook_signature as _verify_webhook_signature


class CertifiedDataPaymentsClient:
    """
    CertifiedData Payments API client.

    Usage::

        client = CertifiedDataPaymentsClient(api_key="cdp_test_...")

        payee = client.payees.create(
            entity_type="company",
            legal_name="Acme Corp",
            idempotency_key="create-payee-acme-001",
        )

    Use ``cdp_test_`` keys for sandbox, ``cdp_live_`` keys for production.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.certifieddata.io",
        api_version: str = "2025-01-01",
        timeout: float = 30.0,
    ) -> None:
        self._http = HttpClient(
            api_key=api_key,
            base_url=base_url,
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
        :param signature_header: ``CDP-Signature`` header value.
        :param timestamp_header: ``CDP-Timestamp`` header value.
        :param secret: Webhook endpoint secret.
        :param tolerance_seconds: Timestamp tolerance in seconds (default 300).
        """
        return _verify_webhook_signature(
            raw_body, signature_header, timestamp_header, secret, tolerance_seconds
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> "CertifiedDataPaymentsClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
