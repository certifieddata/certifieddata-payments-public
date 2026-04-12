# Python SDK

The `certifieddata-agent-commerce` package is the official Python SDK for CertifiedData Agent Commerce.

**Repo path:** [`packages/python-sdk/`](../packages/python-sdk/)

## Install

```bash
pip install certifieddata-agent-commerce
```

## Client setup

```python
from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient

client = CertifiedDataAgentCommerceClient(
    api_key="cdp_live_your_key",
    api_version="2025-01-01",
)
```

### Sandbox / mock server

```python
client = CertifiedDataAgentCommerceClient(
    api_key="cdp_test_your_key",
    api_version="2025-01-01",
    base_url="http://localhost:3456",
)
```

## Create a transaction

```python
tx = client.transactions.create({
    "payment_intent_id": "pi_01HZX8H75Z6X8C5X7JQY6B4M2N",
    "payee_id": "py_01HZX8E77KN1KZ9M2G5D5Q4N4V",
    "amount": 4900,
    "currency": "usd",
    "rail": "stripe",
    "description": "Certified artifact purchase",
})
```

## Attach provenance links

```python
client.transactions.attach_links(tx["id"], {
    "artifact_id": "art_01HXZ7Z8R2QQSN5B3T5VQ4D1WA",
    "certificate_id": "cert_01HXZ803C0R6V4K4P9HWB6J5N6",
    "decision_record_id": "dec_01HXZ80MCP6KNB8M3D0W1MSZV9",
    "provenance_metadata": {
        "cdp:workflow_id": "wf_123",
        "cdp:source_system": "certifieddata-platform",
    },
})
```

## Verify a webhook signature

```python
from certifieddata_agent_commerce.webhooks import verify_signature

is_valid = verify_signature(
    raw_body=raw_body,
    signature_header=request.headers["CDAC-Signature"],
    timestamp_header=request.headers["CDAC-Timestamp"],
    secret=webhook_secret,
)
```

## Pagination

```python
page = client.transactions.list(limit=20)

while page.get("has_more"):
    last_id = page["data"][-1]["id"]
    page = client.transactions.list(limit=20, starting_after=last_id)
```

## Error handling

```python
from certifieddata_agent_commerce.errors import CdpApiError

try:
    client.transactions.create({...})
except CdpApiError as e:
    print(e.code, e.http_status, e.message)
```

## Best use cases

- backend services and scheduled jobs
- workflow orchestration
- reconciliation and audit scripts
- reporting pipelines

## Notes

The Python SDK is synchronous-first in V1. Async support is planned for a future release.

## Related

- [TypeScript SDK](./sdk-typescript.md)
- [Authentication](./authentication.md)
- [Provenance links](./provenance-links.md)
- [Sandbox and mock server](./sandbox-and-mock-server.md)
