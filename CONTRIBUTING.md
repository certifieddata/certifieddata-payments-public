# Contributing

Thank you for your interest in contributing to CertifiedData Payments.

## Before you contribute

Read the following docs in order:

1. [IMPLEMENTATION_RULES.md](./IMPLEMENTATION_RULES.md) — build rules, ID prefixes, money/timestamp conventions
2. [SOURCE_OF_TRUTH.md](./SOURCE_OF_TRUTH.md) — which file is canonical for each surface
3. [PUBLIC_PRIVATE_BOUNDARY.md](./PUBLIC_PRIVATE_BOUNDARY.md) — what belongs here vs in the private platform

## Source-of-truth rule

If you change a resource field, change it in `schemas/resources/{resource}.schema.json` first. OpenAPI and AsyncAPI reference it via `$ref` — do not redefine it elsewhere.

## Consistency check

Before submitting a PR, confirm your change is consistent across:

- JSON Schema (canonical)
- OpenAPI (if a REST-exposed field)
- AsyncAPI (if event-emitted)
- SDK types (derived)
- examples/json (illustrative)
- docs (explanatory)

## Test vectors

If you add a new error code, state transition, or webhook behavior, add a corresponding test vector in `test-vectors/`.

## Enum registries

New enum values go in `schemas/enums/` first. Do not add values only to prose or only to OpenAPI.

## Changesets

This repo uses [changesets](https://github.com/changesets/changesets) for versioning.

Run `pnpm changeset` before your PR to record the change type (patch/minor/major) for affected packages.

## Pull request

- Title: short imperative (e.g. `Add settlement.canceled status to state machine`)
- Body: explain what changed and why; reference the canonical source being updated
