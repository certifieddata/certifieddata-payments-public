# Python SDK

The `certifieddata-payments` package is the official Python SDK for CertifiedData Payments.

## Installation

```bash
pip install certifieddata-payments
```

**Requirements:** Python ≥ 3.9. Uses `httpx` for HTTP and `pydantic` v2 for validation.

## Quick start

```python
from certifieddata_payments import CertifiedDataPaymentsClient

client = CertifiedDataPaymentsClient(api_key="cdp_test_...")

payee = client.payees.create(
    entity_type="company",
    legal_name="Acme Corp",
    idempotency_key="create-payee-acme-001",
)
print(payee["id"])
```

## Client options

| Parameter | Type | Description |
|-----------|------|-------------|
| `api_key` | `str` | Required. Use `cdp_test_` for sandbox, `cdp_live_` for production. |
| `base_url` | `str` | Defaults to `https://api.certifieddata.io`. |
| `api_version` | `str` | Defaults to `2025-01-01`. |
| `timeout` | `float` | Request timeout in seconds (default 30). |

## Context manager

```python
with CertifiedDataPaymentsClient(api_key="cdp_test_...") as client:
    payee = client.payees.create(entity_type="company", ...)
```

## Webhook verification

```python
from certifieddata_payments import verify_webhook_signature

is_valid = verify_webhook_signature(
    raw_body=request.body,
    signature_header=request.headers["CDP-Signature"],
    timestamp_header=request.headers["CDP-Timestamp"],
    secret=os.environ["CDP_WEBHOOK_SECRET"],
)
```

## Resources

| Attribute | Endpoints |
|-----------|-----------|
| `client.payees` | Payees, aliases, payout destinations |
| `client.payment_intents` | Payment intents |
| `client.transactions` | Transactions, attach_links, capture |
| `client.settlements` | Settlements, submit, cancel |
| `client.refunds` | Refunds |
| `client.events` | Events |

## Error handling

```python
from certifieddata_payments import CDPConflictError

try:
    client.transactions.attach_links(tx_id, certificate_id="cert_...")
except CDPConflictError as e:
    if e.code == "provenance.immutable_after_capture":
        # Transaction already captured — provenance is locked
        pass
```

## Note on async

The V1 Python SDK is sync-only. An async variant is planned for a future release.

## Source

[packages/python-sdk/](../packages/python-sdk/)
