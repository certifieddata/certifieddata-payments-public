# certifieddata-agent-commerce

Python SDK for [CertifiedData Agent Commerce](https://certifieddata.io/agent-commerce) — provenance-aware, policy-governed payments for AI agents and artifacts.

## Install

```bash
pip install certifieddata-agent-commerce
```

> **Note:** Install name is `certifieddata-agent-commerce`. Import name is `certifieddata_agent_commerce` (underscore, as required by Python naming conventions).

## Quick start

```python
from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient

# Reads CDAC_API_KEY and CDAC_BASE_URL from environment automatically
client = CertifiedDataAgentCommerceClient()

# Phase 1 — agent declares intent
tx = client.transactions.create(
    amount=2500,       # cents ($25.00)
    currency="usd",
    rail="stripe",
)

# Phase 2 — attach provenance (binds AI decision record to payment)
client.transactions.attach_links(
    tx["id"],
    decision_record_id="dec_abc123",
)

# Phase 3+4 — capture: policy eval → settle → inline signed receipt
capture = client.transactions.capture(tx["id"])
receipt = capture["receipt"]

print(receipt["receipt_id"])
print(receipt["decision_record_id"])
print(receipt["sha256_hash"])
print(receipt["ed25519_sig"])
```

## Configure

```bash
export CDAC_API_KEY=cdp_test_xxx
export CDAC_BASE_URL=https://sandbox.certifieddata.io  # omit for live
```

| Environment | Key prefix   | Base URL                           |
|-------------|--------------|------------------------------------|
| Sandbox     | `cdp_test_`  | `https://sandbox.certifieddata.io` |
| Live        | `cdp_live_`  | `https://certifieddata.io`         |

## Verify receipts publicly

Verification requires no API key:

```bash
curl https://certifieddata.io/api/payments/verify/<receipt_id>
```

Returns:

```json
{
  "valid": true,
  "hashValid": true,
  "signatureValid": true,
  "signingKeyId": "cd_root_2026",
  "signatureAlg": "Ed25519"
}
```

## Local development (mock server)

```bash
# Start mock server on port 3456
pip install flask
python examples/claude-demo/mock_server.py

# Run demo against mock
CDAC_API_KEY=cdp_test_any CDAC_BASE_URL=http://localhost:3456 \
  python examples/claude-demo/demo.py
```

## Receipt shape

Every successful capture returns an inline signed receipt:

```json
{
  "receipt_id": "rcpt_...",
  "transaction_id": "txn_...",
  "policy_id": "pol_...",
  "decision_record_id": "dec_...",
  "sha256_hash": "sha256:...",
  "ed25519_sig": "..."
}
```

`decision_record_id` is the canonical provenance field linking the payment to the AI decision that triggered it.

## Package names

| Context | Name |
|---------|------|
| `pip install` | `certifieddata-agent-commerce` |
| `import` | `certifieddata_agent_commerce` |
| Main class | `CertifiedDataAgentCommerceClient` |

Python requires hyphens in distribution names and underscores in import names — these are the same package, different naming conventions.

## Resources

- [Agent Commerce docs](https://certifieddata.io/agent-commerce)
- [Public repo](https://github.com/certifieddata/certifieddata-agent-commerce-public)
- [OpenAPI spec](https://github.com/certifieddata/certifieddata-agent-commerce-public/blob/main/openapi/certifieddata-agent-commerce-v1.openapi.yaml)
- [Receipt verification](https://certifieddata.io/agent-commerce/payment-verification)

## License

Apache-2.0
