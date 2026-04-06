"""
CertifiedData Payments Python SDK

Provenance-aware payments and settlement for AI artifact commerce.

Usage::

    from certifieddata_payments import CertifiedDataPaymentsClient

    client = CertifiedDataPaymentsClient(api_key="cdp_test_...")

    payee = client.payees.create(
        entity_type="company",
        legal_name="Atlas Synthetic Labs, Inc.",
        idempotency_key="create-payee-001",
    )

See https://github.com/certifieddata/certifieddata-payments-public for full documentation.
"""

from .client import CertifiedDataPaymentsClient
from .errors import (
    CDPError,
    CDPAuthError,
    CDPValidationError,
    CDPNotFoundError,
    CDPConflictError,
    CDPRateLimitError,
)
from .webhooks import verify_webhook_signature

__all__ = [
    "CertifiedDataPaymentsClient",
    "CDPError",
    "CDPAuthError",
    "CDPValidationError",
    "CDPNotFoundError",
    "CDPConflictError",
    "CDPRateLimitError",
    "verify_webhook_signature",
]

__version__ = "0.1.0"
