# CertifiedData Agent Commerce Public Repo — Implementation Rules

## Purpose

This document defines the implementation rules for the public CertifiedData Agent Commerce repository.

The goal of this repo is to expose the public, machine-readable integration surface for CertifiedData Agent Commerce (CDP), including:
- REST API contract
- event contract
- JSON schemas
- SDKs
- mock server
- examples
- docs
- machine-readable discovery artifacts

This repo is for the **public contract layer only**.

---

## Core principle

When there is a choice between:
- prose vs machine-readable artifact
- implicit behavior vs explicit schema
- convenience vs determinism

prefer:
- machine-readable artifact
- explicit schema
- deterministic behavior

---

## Required outputs

The repo must include:

- OpenAPI 3.1 REST contract
- AsyncAPI event contract
- JSON Schemas for common and resource objects
- machine-readable error catalog
- machine-readable capabilities manifest
- machine-readable state machines
- TypeScript SDK
- Python SDK skeleton
- mock server
- JSON examples
- test vectors
- docs
- `llms-full.txt`
- `api-manifest.json`
- `constraints.json`
- `support-matrix.json`

---

## Build rules

1. Generate files in dependency order.
2. Keep all file contents internally consistent.
3. Do not invent unsupported features.
4. Use explicit enums and examples.
5. Avoid vague `metadata: object` patterns unless constrained.
6. Prefer stable IDs and stable field names.
7. All mutating endpoints must support idempotency.
8. All timestamps must be RFC 3339 UTC strings.
9. All money amounts must be integer minor units.
10. All list endpoints must use a consistent pagination envelope.
11. All resources and events must include realistic examples.
12. All event payloads must include version information.
13. All provenance-aware objects must use structured link objects.
14. Public/private boundary must remain strict.

---

## Output rules

When generating files:

- Output one file at a time or in small coherent batches.
- Include complete file contents.
- Avoid placeholder-heavy stubs.
- If a file depends on another not yet generated, note that dependency clearly.
- If uncertain, choose the most explicit and conservative public contract.

---

## Canonical ID prefixes

- `py_` — Payee
- `pya_` — PayeeAlias
- `pydst_` — PayoutDestination
- `cus_` — Customer
- `inv_` — Invoice
- `pi_` — PaymentIntent
- `tx_` — Transaction
- `rcpt_` — Receipt
- `stl_` — Settlement
- `rf_` — Refund
- `evt_` — Event
- `wh_` — WebhookEndpoint
- `idem_` — IdempotencyRecord

Do not invent additional prefixes unless explicitly required.

---

## Machine-readable-first policy

Every major concept should be surfaced in a machine-readable artifact where appropriate.

Examples:
- resource shapes → JSON Schema
- REST operations → OpenAPI
- events → AsyncAPI and/or JSON Schema
- error codes → JSON error catalog
- lifecycle → JSON state machines
- discovery → `api-manifest.json`
- limits → `constraints.json`
- compatibility → `support-matrix.json`
- examples → standalone JSON payload files
- verification behavior → test vectors

---

## Do not invent

Do not invent:
- unsupported payment rails
- hidden compliance fields
- secret handling internals
- raw processor payload passthroughs
- marketplace dispute logic
- tax automation logic
- FX / cross-border settlement features
- treasury internals
- private DB tables or private service objects
- internal payout routing rules
- private policy engine details

If a feature is not explicitly in scope, leave it out or mark it as future work in docs only.

---

## Must include

Every relevant resource, endpoint, event, and SDK surface should include:

- stable ID
- version awareness where relevant
- enum values where relevant
- validation rules
- example payloads
- environment awareness
- idempotency guidance
- lifecycle/state guidance
- provenance behavior if applicable

---

## Consistency rule

The following must agree:

- OpenAPI
- AsyncAPI
- JSON Schemas
- SDK types
- mock server validation
- examples
- docs
- test vectors

No field should be named one way in one surface and differently elsewhere unless intentionally aliased and documented.

---

## Public/private rule

This repository exposes **contract and interface**, not private execution logic.

Public:
- schemas
- contracts
- examples
- SDKs
- docs
- mock behavior

Private:
- payment processor adapters
- secret material
- private treasury logic
- compliance internals
- policy evaluation internals
- internal routing heuristics
- internal settlement math
- private data model internals

If there is uncertainty, err on the side of keeping implementation detail private.
