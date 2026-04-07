# Environments and Versioning

## Environments

CDP supports two environments:

| Environment | Key prefix | `livemode` |
|---|---|---|
| Sandbox | `cdp_test_...` | `false` |
| Live | `cdp_live_...` | `true` |

Sandbox is for development, integration testing, and contract validation.
Live is for production traffic and real settlement behavior.

## Environment boundaries

- keys are environment-specific
- object IDs are environment-scoped and non-portable
- webhook endpoints and secrets are environment-scoped
- sandbox objects must not be treated as live records
- there is no promotion or migration of sandbox data to live

## API versioning

Current documented API version: `2025-01-01`

Send this header on every request:

```http
CDP-API-Version: 2025-01-01
```

If omitted, the API uses the latest version. Pinning the version is strongly recommended for production integrations.

## Version manifest

The root version manifest is machine-readable:

- [`versions.json`](../versions.json)

It records:

- API version string
- schema version
- event schema version
- SDK versions
- compatibility window

## Backward compatibility

Backward-incompatible changes are introduced through explicit versioning. A new API version string indicates a potentially breaking change.

Additive changes (new optional fields, new event types) may be introduced without a version bump. Design webhook consumers and API clients to ignore unknown fields.

## Mock server environment

The mock server always runs in sandbox mode:

```json
{ "livemode": false, "environment": "sandbox" }
```

See [`docs/sandbox-and-mock-server.md`](./sandbox-and-mock-server.md).

## Related

- [Authentication](./authentication.md)
- [Sandbox and mock server](./sandbox-and-mock-server.md)
