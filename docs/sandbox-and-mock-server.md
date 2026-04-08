# Sandbox and Mock Server

CDP provides two development tools: the sandbox API environment and a local mock server.

## Sandbox API

The sandbox environment is a hosted, isolated environment that behaves like live but processes no real payments.

- use `cdp_test_...` API keys
- all responses include `"livemode": false, "environment": "sandbox"`
- object IDs are environment-scoped — sandbox IDs are not valid in live
- webhook delivery works in sandbox with a separate webhook secret

## Mock server

The mock server is a local development tool you run yourself. It simulates the CDP API surface without any network dependency or credentials.

**Repo path:** [`packages/mock-server/`](../packages/mock-server/)

### Start the mock server

```bash
pnpm install
pnpm --filter @certifieddata/agent-commerce-mock-server start
```

### Health check

```bash
curl http://localhost:3456/v1/health
```

Expected response:

```json
{ "status": "ok", "mode": "mock", "livemode": false }
```

### Capabilities endpoint

```bash
curl http://localhost:3456/v1/capabilities
```

Returns: [`schemas/capabilities/capabilities.json`](../schemas/capabilities/capabilities.json)

### Version endpoint

```bash
curl http://localhost:3456/v1/version
```

Returns: [`versions.json`](../versions.json)

## Mock server behavior

The mock server:

- validates all requests against JSON Schemas via AJV
- returns deterministic IDs (`py_test_0001`, `py_test_0002`, etc.)
- implements idempotency key tracking per session
- emits in-memory events consumable via `GET /v1/events`
- always returns `livemode: false`

The mock server does **not**:

- deliver real webhook payloads to external URLs
- process real payments
- simulate compliance or KYC behavior

## Supported resources in mock server

See [`support-matrix.json`](../support-matrix.json) for which resources are available in the mock server vs live API.

## Use cases

Use the mock server to:

- validate auth and version header behavior
- test request and response structure
- exercise webhook signature verification
- build SDK integrations before credentials exist
- validate your own examples against a stable development target

## Connecting an SDK to the mock server

### TypeScript

```ts
const client = new CertifiedDataAgentCommerceClient({
  apiKey: "cdp_test_any",
  apiVersion: "2025-01-01",
  baseUrl: "http://localhost:3456",
});
```

### Python

```python
client = CertifiedDataAgentCommerceClient(
    api_key="cdp_test_any",
    api_version="2025-01-01",
    base_url="http://localhost:3456",
)
```

## Differences between mock server and sandbox

| Behavior | Mock server | Sandbox API |
|---|---|---|
| Runs locally | Yes | No |
| Requires credentials | No | Yes |
| Real webhook delivery | No | Yes |
| Idempotency tracking | Per-session | Persistent (24h) |
| Data persistence | In-memory | Persistent |
| ID format | Counter-based | ULID-style |

## Related

- [Authentication](./authentication.md)
- [Environments and versioning](./environments-and-versioning.md)
- [Errors and idempotency](./errors-and-idempotency.md)
- [Test vectors](../test-vectors/)
