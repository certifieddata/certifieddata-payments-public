# CertifiedData Agent Commerce — Public SDK & Contract

AI agents can complete policy-governed payments. Each successful payment returns a cryptographic receipt. Receipts are independently verifiable — no dashboard, no trust required.

---

## Install

```bash
# TypeScript / Node.js
pnpm add @certifieddata/payments
# or: npm install @certifieddata/payments

# Python
pip install certifieddata-payments
```

## Configure

```bash
export CDP_API_KEY=cdp_test_xxx
export CDP_BASE_URL=https://sandbox.certifieddata.io
```

Sandbox keys start with `cdp_test_`. Live keys start with `cdp_live_`.

## Run a payment

```ts
import { CertifiedDataPaymentsClient } from "@certifieddata/payments";

const client = new CertifiedDataPaymentsClient({
  // reads CDP_API_KEY + CDP_BASE_URL from env automatically
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
from certifieddata_payments import CertifiedDataPaymentsClient

# reads CDP_API_KEY + CDP_BASE_URL from env automatically
client = CertifiedDataPaymentsClient()

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

Verification is public and machine-checkable — no API key needed:

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

This is not just a webhook log or dashboard entry. The receipt is independently verifiable off-platform.

---

## Canonical receipt shape

Every successful capture returns a signed receipt inline:

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

No second fetch needed. The receipt is always inlined on capture.

---

## Local development

Run the mock server for development without sandbox credentials:

```bash
pnpm install
pnpm --filter @certifieddata/payments-mock-server start
# → http://localhost:3456
```

```bash
CDP_API_KEY=cdp_test_any CDP_BASE_URL=http://localhost:3456 \
  node examples/claude-demo/demo.mjs
```

---

## What this repository contains

| Path | Contents |
|------|----------|
| `openapi/` | OpenAPI 3.1 REST contract |
| `asyncapi/` | AsyncAPI event/webhook contract |
| `schemas/` | JSON Schemas — resources, enums, lifecycle state machines, errors |
| `packages/typescript-sdk/` | `@certifieddata/payments` TypeScript SDK |
| `packages/python-sdk/` | `certifieddata-payments` Python SDK |
| `packages/mock-server/` | Local mock server for development |
| `examples/claude-demo/` | Runnable end-to-end demo (Python + TypeScript) |
| `examples/` | JSON payload examples and runnable scripts |
| `test-vectors/` | Machine-readable test vectors |
| `docs/` | Markdown documentation |
| `api-manifest.json` | Machine discovery entrypoint |
| `llms.txt` | LLM-readable discovery index |

---

## Run the end-to-end demo

```bash
# Python
pip install certifieddata-payments
CDP_API_KEY=cdp_test_xxx CDP_BASE_URL=https://sandbox.certifieddata.io \
  python examples/claude-demo/demo.py

# TypeScript
pnpm install
CDP_API_KEY=cdp_test_xxx CDP_BASE_URL=https://sandbox.certifieddata.io \
  pnpm --filter @certifieddata/payments-demo start
```

The demo runs all 5 phases and prints the signed receipt + independent verification result.

---

## Environments

| Environment | Key prefix | Base URL |
|-------------|------------|----------|
| Sandbox | `cdp_test_` | `https://sandbox.certifieddata.io` |
| Live | `cdp_live_` | `https://certifieddata.io` |

---

## Machine-readable contract

The canonical sources of truth are:

- **REST API** → `openapi/certifieddata-payments-v1.openapi.yaml`
- **Events** → `asyncapi/certifieddata-payments-events-v1.asyncapi.yaml`
- **Resource shapes** → `schemas/resources/*.schema.json`
- **Lifecycle rules** → `schemas/state-machines/*.json`
- **Discovery** → `api-manifest.json`

---

## Related

- [CertifiedData.io](https://certifieddata.io)
- [Agent Commerce docs](https://certifieddata.io/agent-commerce)
- [Receipt verification](https://certifieddata.io/agent-commerce/authorization)
