# Capabilities

The capabilities endpoint returns a machine-readable manifest describing what the CDP API supports in the current environment.

## Machine-readable references

- Canonical: [schemas/capabilities/capabilities.json](../schemas/capabilities/capabilities.json)
- Constraints: [constraints.json](../constraints.json)
- Support matrix: [support-matrix.json](../support-matrix.json)

## Endpoint

```
GET /v1/capabilities
```

Returns the capabilities manifest. The canonical definition is in [schemas/capabilities/capabilities.json](../schemas/capabilities/capabilities.json) — the API response matches that shape exactly.

## Also available

```
GET /v1/health     → { status, mode, livemode, api_version, timestamp }
GET /v1/version    → versions.json content
GET /v1/openapi.json → OpenAPI spec (JSON format)
```

## TypeScript SDK

```typescript
const capabilities = await client.capabilities.get();
const health = await client.capabilities.health();
const version = await client.capabilities.version();
```

## Key fields

| Field | Description |
|-------|-------------|
| `payment_rails` | Supported rails in this environment |
| `event_types` | All supported event type strings |
| `provenance_link_types` | Supported provenance link fields |
| `idempotency.header_name` | `Idempotency-Key` |
| `pagination.default_limit` | 20 |
| `pagination.max_limit` | 100 |
| `webhooks.signature_algorithm` | `hmac-sha256` |
| `webhooks.signature_header` | `CDP-Signature` |

Agents should prefer [schemas/capabilities/capabilities.json](../schemas/capabilities/capabilities.json) as the static source of truth, and use `GET /v1/capabilities` to confirm runtime environment support.
