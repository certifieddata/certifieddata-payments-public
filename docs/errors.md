# Errors

All CDP errors use a consistent JSON shape:

```json
{
  "error": {
    "code": "auth.invalid_api_key",
    "message": "The API key provided is invalid.",
    "http_status": 401,
    "retryable": false,
    "docs_url": "/docs/errors.md#authinvalid_api_key"
  }
}
```

## Machine-readable error catalog

The canonical error catalog is at [`schemas/errors/error-catalog.json`](../schemas/errors/error-catalog.json).

## Common errors

### `auth.invalid_api_key` (401)
The API key is invalid. Use a valid `cdp_test_` or `cdp_live_` key.

### `auth.environment_mismatch` (403)
The API key environment does not match the requested resource. Use sandbox keys for sandbox resources and live keys for live resources.

### `validation.invalid_request` (400)
The request body is invalid. Check field names, types, and required values. The response includes a `validation_errors` array.

### `idempotency.key_reused_with_different_payload` (409)
An idempotency key was reused with a different request payload. Reuse a key only with the exact same payload.

### `state.invalid_transition` (409)
The requested state transition is not allowed. Check the relevant state machine in [`schemas/state-machines/`](../schemas/state-machines/).

### `provenance.immutable_after_capture` (409)
Provenance links cannot be modified after a transaction is captured. Attach links before capture.

### `webhooks.invalid_signature` (400)
The webhook signature is invalid. Recompute HMAC-SHA256 using `{timestamp}.{payload}` as the signed data.

### `resource.not_found` (404)
The resource was not found. Verify the ID and environment. IDs are environment-scoped.

### `rate_limit.exceeded` (429)
Rate limit exceeded. Back off and retry with exponential backoff.

## Retryable errors

Only `rate_limit.exceeded` is retryable. All other errors indicate a problem with the request that must be corrected before retrying.
