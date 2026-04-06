# Authentication

## API Keys

CDP uses bearer token authentication.

```
Authorization: Bearer cdp_test_...   # sandbox
Authorization: Bearer cdp_live_...   # live
```

Key prefixes encode the environment:
- `cdp_test_` — sandbox (`livemode: false`)
- `cdp_live_` — live (`livemode: true`)

## API Version header

Always pass the API version header:

```
CDP-API-Version: 2025-01-01
```

## Idempotency

All mutating POST endpoints require an idempotency key:

```
Idempotency-Key: your-unique-key-here
```

See [Idempotency](./idempotency.md) for details.

## Environment isolation

Sandbox and live resources are non-portable. A sandbox `py_test_...` ID will not resolve against the live API. Always use matching keys for the environment you intend to target.

## Webhook signatures

Webhook delivery uses HMAC-SHA256 signatures. See [Webhooks](./webhooks.md) for the signature verification protocol.
