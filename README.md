# CertifiedData Agent Commerce — Public SDK & Contract

![Image](https://github.com/user-attachments/assets/0b1ff84d-f9b7-491e-9c6c-e8f00d862e0e)

AI agents can complete policy-governed payments. Each successful capture returns an inline signed receipt, and that receipt is independently verifiable with Ed25519 + SHA-256 — no dashboard or private console required.

---

## Install

```bash
# TypeScript / Node.js
pnpm add @certifieddata/payments
# or: npm install @certifieddata/payments

# Python
pip install certifieddata-agent-commerce
```

> **Python naming note:** Install name is `certifieddata-agent-commerce` (hyphens). Import name is `certifieddata_agent_commerce` (underscores). This is standard Python convention — they refer to the same package.

## Configure

Get your keys at [certifieddata.io/dashboard/cdp/api-keys](https://certifieddata.io/dashboard/cdp/api-keys).

```bash
export CDAC_API_KEY=cdp_test_xxx
# CDAC_BASE_URL defaults to https://certifieddata.io — omit unless running a local mock
```

Test keys start with `cdp_test_`. Live keys start with `cdp_live_`. Both work against the same host — the key prefix controls which environment the request is routed to.

## Run a payment

```ts
import { CertifiedDataAgentCommerceClient } from "@certifieddata/payments";

const client = new CertifiedDataAgentCommerceClient({
  // reads CDAC_API_KEY + CDAC_BASE_URL from env automatically
});

// Phase 1 — agent declares intent
const tx = await client.transactions.create({
  amount:   2500,   // cents ($25.00)
  currency: "usd",
  rail:     "stripe",
  merchant_reference: "order-1001",
});

// Phase 2 — attach provenance (optional but recommended)
await client.transactions.attachLinks(tx.id, {
  decision_record_id: "dec_abc123",
});

// Phase 3 — capture: policy eval → settlement → inline signed receipt
const capture = await client.transactions.capture(tx.id);
console.log(capture.receipt);
```

```python
from certifieddata_agent_commerce import CertifiedDataAgentCommerceClient

# reads CDAC_API_KEY + CDAC_BASE_URL from env automatically
client = CertifiedDataAgentCommerceClient()

tx = client.transactions.create(
    amount=2500,   # cents
    currency="usd",
    rail="stripe",
)

capture = client.transactions.capture(tx["id"])
receipt = capture["receipt"]
print(receipt)
```

## Verify publicly

Verification is public, independent, and machine-checkable — no API key needed:

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

This is not just a webhook log or dashboard entry. It is a machine-verifiable receipt that can be checked off-platform with the public verify route.

---

## Canonical receipt shape

Every successful capture returns an inline signed receipt:

```json
{
  "transaction_id": "txn_123",
  "status": "captured",
  "receipt": {
    "receipt_id": "rcpt_123",
    "transaction_id": "txn_123",
    "policy_id": "pol_123",
    "decision_record_id": "dec_123",
    "sha256_hash": "abc...",
    "ed25519_sig": "xyz..."
  }
}
```

No second fetch is required. The receipt is returned inline on capture, and the demo binds decision lineage with `decision_record_id`.

---

## Local development

Run locally without sandbox credentials:

```bash
pnpm install
pnpm --filter @certifieddata/agent-commerce-mock-server start
# → http://localhost:3456
```

```bash
# self-contained Flask mock used by the public demo flow
pip install flask
python examples/claude-demo/mock_server.py
# → http://localhost:3456
```

```bash
# local demo
CDAC_API_KEY=cdp_test_any CDAC_BASE_URL=http://localhost:3456 \
  pnpm exec tsx examples/claude-demo/demo.ts

CDAC_API_KEY=cdp_test_any CDAC_BASE_URL=http://localhost:3456 \
  python examples/claude-demo/demo.py
```

```bash
# test against live API with a test key (get key from dashboard)
CDAC_API_KEY=cdp_test_xxx \
  pnpm exec tsx examples/claude-demo/demo.ts

CDAC_API_KEY=cdp_test_xxx \
  python examples/claude-demo/demo.py
```

---

## What this repository contains

| Path | Contents |
|------|----------|
| `openapi/` | OpenAPI 3.1 REST contract |
| `asyncapi/` | AsyncAPI event/webhook contract |
| `schemas/` | JSON Schemas — resources, enums, lifecycle state machines, errors |
| `packages/typescript-sdk/` | `@certifieddata/payments` TypeScript SDK |
| `packages/python-sdk/` | `certifieddata-agent-commerce` Python SDK |
| `packages/mock-server/` | Local mock server for development |
| `examples/claude-demo/` | Runnable end-to-end demo (Python + TypeScript) |
| `examples/` | JSON payload examples and runnable scripts |
| `test-vectors/` | Machine-readable test vectors |
| `docs/` | Markdown documentation |
| `api-manifest.json` | Machine discovery entrypoint |
| `llms.txt` | LLM-readable discovery index |

---

## Run the end-to-end demo

Get a test key at [certifieddata.io/dashboard/cdp/api-keys](https://certifieddata.io/dashboard/cdp/api-keys), then:

```bash
# Python
pip install certifieddata-agent-commerce
CDAC_API_KEY=cdp_test_xxx python examples/claude-demo/demo.py

# TypeScript
pnpm install
CDAC_API_KEY=cdp_test_xxx pnpm exec tsx examples/claude-demo/demo.ts
```

Or run fully offline against the local mock (no key required):

```bash
pip install flask && python examples/claude-demo/mock_server.py
CDAC_API_KEY=cdp_test_any CDAC_BASE_URL=http://localhost:3456 python examples/claude-demo/demo.py
```

The demo runs all 5 phases, returns an inline signed receipt from capture, confirms `decision_record_id` is present in the signed payload, and verifies the receipt independently via the public verify route.

---

## Environments

| Environment | Key prefix | Base URL |
|-------------|------------|----------|
| Test | `cdp_test_` | `https://certifieddata.io` |
| Live | `cdp_live_` | `https://certifieddata.io` |

Both test and live keys route through `https://certifieddata.io`. The key prefix (`cdp_test_` vs `cdp_live_`) determines the environment. There is no separate sandbox hostname. Get keys at [certifieddata.io/dashboard/cdp/api-keys](https://certifieddata.io/dashboard/cdp/api-keys).

---

## Machine-readable contract

The canonical sources of truth are:

- **REST API** → `openapi/certifieddata-agent-commerce-v1.openapi.yaml`
- **Events** → `asyncapi/certifieddata-agent-commerce-events-v1.asyncapi.yaml`
- **Resource shapes** → `schemas/resources/*.schema.json`
- **Lifecycle rules** → `schemas/state-machines/*.json`
- **Discovery** → `api-manifest.json`

---

## Related

- [CertifiedData.io](https://certifieddata.io)
- [Agent Commerce docs](https://certifieddata.io/agent-commerce)
- [Receipt verification](https://certifieddata.io/agent-commerce/authorization)
