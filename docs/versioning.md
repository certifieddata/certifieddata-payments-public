# Versioning

## API versioning

CertifiedData Agent Commerce uses date-based API versioning.

Current version: `2025-01-01`

Pass the version in every request:
```
CDAC-API-Version: 2025-01-01
```

SDKs send this header automatically.

## Machine-readable version manifest

All version strings are centralized in [versions.json](../versions.json):

| Field | Description |
|-------|-------------|
| `api_version` | Date string for the REST/event contract |
| `schema_version` | Semver for JSON Schema definitions |
| `event_schema_version` | Semver for AsyncAPI event contract |
| `sdk_versions` | Per-language SDK versions |

The API also exposes this at `GET /v1/version`.

## Backwards compatibility

CDP follows a stable-by-default policy:
- Breaking changes require a new API version date
- Additive changes (new optional fields, new event types) may be introduced without a version bump
- Deprecated fields are annotated in the OpenAPI spec and kept for at least one version window

## Schema versioning

JSON Schemas are versioned with semver in their `version` field. The canonical source is [schemas/](../schemas/).

## Event versioning

All events include `event_version` (e.g. `"1.0.0"`). The event envelope shape is stable within an API version.

## SDK versioning

SDKs follow semver independently of the API version. See [versions.json](../versions.json) for current SDK versions.
