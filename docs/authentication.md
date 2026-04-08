# Authentication

CDP authenticates requests using API keys and explicit API version headers.

## API keys

Supported key formats:

- Sandbox: `cdp_test_...`
- Live: `cdp_live_...`

Pass the key in the Authorization header:

```http
Authorization: Bearer cdp_test_xxx
```

## API versioning

Send the version header on every request:

```http
CDAC-API-Version: 2025-01-01
```

If the header is omitted, the API uses the latest version. Pinning the version is strongly recommended for production integrations.

## Environment rules

- sandbox keys only work in sandbox
- live keys only work in live environments
- object IDs are environment-scoped and non-portable
- webhook secrets are environment-scoped
- test data must not be assumed valid in live mode

## Security guidance

- never expose live API keys in client-side browser code
- store credentials in environment variables or a secrets manager
- rotate credentials on a fixed schedule
- maintain separate webhook consumers for sandbox and live environments
- treat `cdp_live_` keys as production secrets with equivalent access controls

## Related

- [Environments and versioning](./environments-and-versioning.md)
- [Webhooks](./webhooks.md)
