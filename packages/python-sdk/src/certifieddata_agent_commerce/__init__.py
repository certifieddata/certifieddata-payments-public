"""
CertifiedData Agent Commerce Python SDK

Provenance-aware payments and settlement for AI artifact commerce.

Usage::

    from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient

    client = CertifiedDataAgentCommerceClient(api_key="cdp_test_...")

    payee = client.payees.create(
        entity_type="company",
        legal_name="Atlas Synthetic Labs, Inc.",
        idempotency_key="create-payee-001",
    )

See https://github.com/certifieddata/certifieddata-agent-commerce-public for full documentation.
"""

from .client import CertifiedDataAgentCommerceClient
from .errors import (
    CDACError,
    CDACAuthError,
    CDACValidationError,
    CDACNotFoundError,
    CDACConflictError,
    CDACRateLimitError,
)
from .webhooks import verify_webhook_signature

__all__ = [
    "CertifiedDataAgentCommerceClient",
    "CDACError",
    "CDACAuthError",
    "CDACValidationError",
    "CDACNotFoundError",
    "CDACConflictError",
    "CDACRateLimitError",
    "verify_webhook_signature",
]

__version__ = "0.1.0"
