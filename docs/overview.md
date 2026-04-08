# CertifiedData Agent Commerce — Overview

CertifiedData Agent Commerce (CDP) is a provenance-aware payments and settlement API for certified AI artifacts.

CDP helps developers, platforms, and machine actors create commercial events that stay linked to the artifacts, certificates, datasets, and decision records they fund.

## What CDP does

CDP provides:

- payee onboarding and payout destination records
- customers, invoices, payment intents, and transactions
- settlements and refunds
- provenance links to artifacts, certificates, and decisions
- webhook and event delivery for lifecycle changes
- sandbox and mock-server support for integration testing

## Public repo and contracts

Canonical public repo:

- `https://github.com/certifieddata/certifieddata-agent-commerce-public`

Canonical machine-readable contracts:

- REST API: [`openapi/certifieddata-agent-commerce-v1.openapi.yaml`](../openapi/certifieddata-agent-commerce-v1.openapi.yaml)
- Events/Webhooks: [`asyncapi/certifieddata-agent-commerce-events-v1.asyncapi.yaml`](../asyncapi/certifieddata-agent-commerce-events-v1.asyncapi.yaml)
- Schemas: [`schemas/`](../schemas/)
- Discovery manifest: [`api-manifest.json`](../api-manifest.json)

## SDKs

- TypeScript SDK: [`packages/typescript-sdk/`](../packages/typescript-sdk/)
- Python SDK: [`packages/python-sdk/`](../packages/python-sdk/)

## Core idea: provenance-aware commerce

A normal payment tells you money moved.

A CDP transaction can also tell you:

- what artifact or service was purchased
- what certificate or attestation applied
- what decision record or policy reference was attached
- what settlement or refund happened later
- what machine-readable proof exists for reconciliation

## Design principles

- machine-readable first
- explicit lifecycle states
- idempotent writes
- stable, environment-scoped identifiers
- provenance links as first-class fields
- SDKs that map directly to the public contract

## Where to start

For most teams:

1. read [`docs/quickstart.md`](./quickstart.md)
2. install an SDK
3. run the mock server
4. inspect the OpenAPI and AsyncAPI contracts
5. integrate webhooks and idempotent writes

## Docs index

| Doc | Contents |
|---|---|
| [quickstart.md](./quickstart.md) | Get running in minutes |
| [authentication.md](./authentication.md) | API keys and versioning |
| [api-resources.md](./api-resources.md) | Resource types and relationships |
| [provenance-links.md](./provenance-links.md) | Linking payments to artifacts and certificates |
| [webhooks.md](./webhooks.md) | Event delivery and signature verification |
| [sdk-typescript.md](./sdk-typescript.md) | TypeScript SDK reference |
| [sdk-python.md](./sdk-python.md) | Python SDK reference |
| [environments-and-versioning.md](./environments-and-versioning.md) | Sandbox, live, and API versioning |
| [pricing-and-plans.md](./pricing-and-plans.md) | Plan tiers and billing behavior |
| [errors-and-idempotency.md](./errors-and-idempotency.md) | Error codes and safe retries |
| [sandbox-and-mock-server.md](./sandbox-and-mock-server.md) | Local development with mock server |
