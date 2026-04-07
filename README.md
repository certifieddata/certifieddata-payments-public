# CertifiedData Payments — Public SDK & Contract

**Provenance-aware payments and settlement for certified AI artifacts.**

CertifiedData Payments (CDP) is a commerce and settlement layer built for the [CertifiedData](https://certifieddata.io) ecosystem. It enables provenance-linked transactions — payments that carry verifiable references to the AI artifacts, certificates, datasets, and decisions they fund.

---

## Public routes

- **Public repo**: `https://github.com/certifieddata/certifieddata-payments-public`
- **Docs index**: `./docs/overview.md`
- **REST contract**: `./openapi/certifieddata-payments-v1.openapi.yaml`
- **Events/webhooks**: `./asyncapi/certifieddata-payments-events-v1.asyncapi.yaml`
- **TypeScript SDK**: `./packages/typescript-sdk/`
- **Python SDK**: `./packages/python-sdk/`
- **Mock server**: `./packages/mock-server/`
- **Examples**: `./examples/`
- **Discovery manifest**: `./api-manifest.json`

---

## What this repository contains

| Directory | Contents |
|---|---|
| `openapi/` | OpenAPI 3.1 REST contract |
| `asyncapi/` | AsyncAPI event/webhook contract |
| `schemas/` | JSON Schemas for resources, primitives, enums, lifecycle states, errors, and capabilities |
| `packages/typescript-sdk/` | `@certifieddata/payments` TypeScript SDK |
| `packages/python-sdk/` | `certifieddata-payments` Python SDK |
| `packages/mock-server/` | Local mock server for development and testing |
| `examples/` | JSON payloads and runnable examples |
| `test-vectors/` | Machine-readable test vectors for webhooks, idempotency, and provenance |
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
pnpm install
pnpm --filter @certifieddata/payments-mock-server start
curl http://localhost:3456/v1/health
```

Expected:

```json
{ "status": "ok", "mode": "mock", "livemode": false }
```

See:

- [Overview](./docs/overview.md)
- [Quickstart](./docs/quickstart.md)
- [Authentication](./docs/authentication.md)
- [TypeScript SDK](./docs/sdk-typescript.md)
- [Python SDK](./docs/sdk-python.md)
- [Webhooks](./docs/webhooks.md)

---

## SDK install

```bash
pnpm add @certifieddata/payments
pip install certifieddata-payments
```

---

## API version

Current API version: `2025-01-01`

Send:

```http
CDP-API-Version: 2025-01-01
```

---

## Environments

- **Sandbox**: `cdp_test_...` API keys, `livemode: false`
- **Live**: `cdp_live_...` API keys, `livemode: true`

IDs and credentials are environment-scoped and non-portable.

---

## Related

- [CertifiedData.io](https://certifieddata.io)
- [Docs overview](./docs/overview.md)
- [Machine discovery manifest](./api-manifest.json)
