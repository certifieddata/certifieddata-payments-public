# CertifiedData Payments — Source of Truth Hierarchy

## Purpose

Defines the source-of-truth hierarchy to prevent drift across OpenAPI, AsyncAPI, JSON Schemas, SDK types, mock server validation, docs, examples, and test vectors.

---

## Source of truth hierarchy

### 1. REST surface
**Canonical source:** OpenAPI 3.1

File: `openapi/certifieddata-payments-v1.openapi.yaml`

Source of truth for: endpoints, methods, parameters, headers, request/response contracts, auth model, pagination structure, examples embedded in operations.

### 2. Event surface
**Canonical source:** AsyncAPI

File: `asyncapi/certifieddata-payments-events-v1.asyncapi.yaml`

Source of truth for: event envelope, event types, webhook payload structure, delivery metadata, header expectations, event examples.

### 3. Shared data models
**Canonical source:** JSON Schemas

Files: `schemas/common/*.json` and `schemas/resources/*.json`

These are canonical shared component definitions referenced by OpenAPI, AsyncAPI, SDK generation, mock server validation, examples, and docs. Shared model definitions should not be redefined inconsistently elsewhere.

### 4. Lifecycle rules
**Canonical source:** JSON state machine definitions

Files: `schemas/state-machines/*.json`

Canonical for: allowed states, transitions, terminal states, forbidden transitions. Used by docs, tests, mock server, and validation helpers.

### 5. Operational constraints
**Canonical source:** constraints file

File: `constraints.json`

Canonical for: max lengths, pagination limits, timestamp tolerances, metadata limits, idempotency limits, and other operational bounds.

### 6. Error taxonomy
**Canonical source:** error catalog

File: `schemas/errors/error-catalog.json`

Canonical for: error codes, categories, retryability, HTTP status mapping, machine guidance.

### 7. Capability discovery
**Canonical source:** capabilities manifest

File: `schemas/capabilities/capabilities.json`

Canonical for: supported resources, rails, event types, environment support, limits references, SDK availability, feature flags.

### 8. Discovery map
**Canonical source:** API manifest

File: `api-manifest.json`

Entrypoint for machines to find: OpenAPI, AsyncAPI, JSON Schemas, errors, capabilities, state machines, constraints, examples, test vectors, docs.

---

## Derived artifacts

The following should be derived from canonical artifacts and must remain consistent with them:

- SDK resource types
- SDK method docs
- mock server validators
- docs pages
- examples
- fixtures
- `llms-full.txt`

---

## Rule

Human-readable docs (markdown) are explanatory and supportive. They are **not** canonical for field names, enum sets, endpoint semantics, event shapes, limits, or state transitions.

`llms-full.txt` is a machine-facing navigation layer. It points to canonical artifacts — it is not a replacement for them.

If the same concept appears in multiple places:
1. identify the canonical source above
2. ensure all secondary surfaces match it
3. do not silently introduce drift
