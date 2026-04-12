# CertifiedData Agent Commerce — Public / Private Boundary

## Purpose

This document defines what belongs in the public CertifiedData Agent Commerce repository and what must remain private.

The public repo is intended to be published and consumed by:
- developers
- platforms
- partners
- machine agents
- SDK users
- docs readers

It is not a mirror of the private payments backend.

---

## Public repo includes

### Public API surface
- OpenAPI 3.1 spec
- documented REST endpoints
- request/response schemas
- standard headers
- idempotency semantics
- authentication model
- pagination model

### Public event surface
- AsyncAPI event schema
- event envelope definition
- event type catalog
- webhook delivery semantics
- webhook signature contract
- webhook test vectors

### Public object model
- payees, aliases, payout destinations
- customers, invoices
- payment intents, transactions
- settlements, refunds
- webhook endpoints, events
- provenance link structures
- idempotency records (public contract shape only)

### Public SDKs and tooling
- TypeScript SDK, Python SDK skeleton
- mock server, examples, docs
- machine-readable discovery files

### Public machine-readable artifacts
- JSON Schemas, error catalog, capabilities manifest
- state machine definitions, constraints manifest
- support matrix, JSON fixtures and test vectors
- `llms-full.txt`, `api-manifest.json`

---

## Private repo keeps

### Secrets and trust material
- Stripe secret keys, webhook secrets
- Ed25519 private keys, PEM files
- secret rotation internals

### Internal payments execution logic
- Stripe adapter code, onchain adapter internals
- internal treasury routing, settlement netting rules
- payout calculation internals, retry policies
- risk flags not intended for public exposure

### Internal compliance and policy systems
- KYC / AML integrations, sanctions screening
- processor-specific compliance payloads
- internal review queues, blocked/flagged reasoning
- policy engine internals, private evaluation code

### Private persistence model
- DB migrations, raw DB schema internals
- internal table definitions and joins

### Internal operational tooling
- admin endpoints, operator controls
- manual override tooling, support tooling
- internal reconciliation dashboards

---

## Public abstraction philosophy

The public repo should expose stable abstractions, not processor internals.

Good public abstraction:
- `rail: "stripe" | "usdc_base" | "usdc_ethereum" | "eth_ethereum"`
- `status: "created" | "captured" | "succeeded" | "failed"`

Bad public leakage:
- raw processor payload blobs
- internal compliance result objects
- internal routing scores
- processor-specific private error payloads

---

## Provenance boundary

Public: artifact_id, certificate_id, decision_record_id, dataset_id, model_id, output_id, receipt_hash, external_reference, constrained provenance_metadata

Not public: internal signing key details, raw private attestation internals, internal evidence storage mechanisms

---

## SDK boundary

SDKs expose: typed resource methods, request options, idempotency helpers, webhook signature verification helpers, pagination helpers, error classes

SDKs do not expose: internal service clients, processor-specific private clients, admin-only methods, direct secret rotation methods

---

## Mock server boundary

Mock server may simulate: object creation, basic lifecycle transitions, idempotency behavior, event emission, validation behavior, sandbox responses

Mock server must not simulate: real money movement, private routing decisions, compliance internals, production settlement math, secret material handling

---

## Rule of thumb

If a feature is necessary for an external integrator to understand or consume the public CDP contract, it may belong in the public repo.

If a feature reveals internal execution logic, secrets, compliance internals, or operational controls, it must remain private.
