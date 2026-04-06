# CertifiedData Payments — Public SDK & Contract

**Provenance-aware payments and settlement for certified AI artifacts.**

CertifiedData Payments (CDP) is a commerce and settlement layer built for the [CertifiedData](https://certifieddata.io) ecosystem. It enables provenance-linked transactions — payments that carry verifiable references to the AI artifacts, certificates, datasets, and decisions they fund.

---

## What this repository contains

| Directory | Contents |
|---|---|
| `openapi/` | OpenAPI 3.1 REST contract |
| `asyncapi/` | AsyncAPI event/webhook contract |
| `schemas/` | JSON Schemas (resources, common primitives, enums, state machines, errors, capabilities) |
| `packages/typescript-sdk/` | `@certifieddata/payments` TypeScript SDK |
| `packages/python-sdk/` | `certifieddata-payments` Python SDK |
| `packages/mock-server/` | Local mock server for development and testing |
| `examples/` | JSON payloads and runnable code examples |
| `test-vectors/` | Machine-readable test vectors (webhook signature, idempotency, provenance) |
| `docs/` | Markdown documentation |
| `api-manifest.json` | Root machine-discovery entrypoint |
| `constraints.json` | Canonical operational limits |
| `support-matrix.json` | Feature support across environments and SDKs |
| `llms-full.txt` | Machine-facing repository guide |

---

## What this repository does NOT contain

- Payment processor secrets or webhook signing secrets
- Internal routing or treasury logic
- Compliance internals or KYC/AML integrations
- Private DB schema or private service implementations

---

## Machine-readable-first

The canonical sources of truth are:

- **REST API** → `openapi/certifieddata-payments-v1.openapi.yaml`
- **Events/webhooks** → `asyncapi/certifieddata-payments-events-v1.asyncapi.yaml`
- **Resource shapes** → `schemas/resources/*.schema.json`
- **Lifecycle rules** → `schemas/state-machines/*.json`
- **Discovery** → `api-manifest.json`

Start there. Markdown docs are explanatory supplements, not the source of truth.

---

## Quick start

```bash
# Install dependencies
pnpm install

# Start mock server
pnpm --filter @certifieddata/payments-mock-server start

# GET /v1/health
curl http://localhost:3456/v1/health
# → { "status": "ok", "mode": "mock", "livemode": false }
```

---

## SDK install

```bash
# TypeScript
pnpm add @certifieddata/payments

# Python
pip install certifieddata-payments
```

---

## Core concept: Provenance linking

CDP is built around provenance-aware commerce. Every transaction can be linked to the artifact, certificate, dataset, model, or decision it funds:

```typescript
await client.transactions.attachLinks("tx_...", {
  artifact_id: "art_...",
  certificate_id: "cert_...",
  decision_id: "dec_...",
  provenance_metadata: {
    "cdp:workflow_id": "wf_123",
    "partner:invoice_ref": "INV-44821"
  }
});
```

---

## API version

Current API version: `2025-01-01`

Pass as a header: `CDP-API-Version: 2025-01-01`

---

## Environments

- **Sandbox**: `cdp_test_...` API keys, `livemode: false`
- **Live**: `cdp_live_...` API keys, `livemode: true`

IDs and credentials are environment-scoped and non-portable.

---

## Related

- [CertifiedData.io](https://certifieddata.io) — AI artifact certification platform
- [API reference](./docs/overview.md)
- [Machine discovery manifest](./api-manifest.json)
