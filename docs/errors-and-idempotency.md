# Errors and Idempotency

## Error shape

All CDP errors return a consistent JSON structure:

```json
{
  "code": "idempotency.key_reused_with_different_payload",
  "http_status": 409,
  "message": "The idempotency key was already used with a different request payload.",
  "retryable": false,
  "docs_url": "/docs/errors-and-idempotency.md"
}
```

## Error catalog

Machine-readable error catalog: [`schemas/errors/error-catalog.json`](../schemas/errors/error-catalog.json)

## Common error codes

| Code | HTTP | Retryable | Meaning |
|---|---|---|---|
| `auth.invalid_api_key` | 401 | No | API key is invalid or missing |
| `auth.environment_mismatch` | 403 | No | Key environment does not match resource environment |
| `validation.invalid_request` | 400 | No | Request body failed validation |
| `idempotency.key_reused_with_different_payload` | 409 | No | Same idempotency key used with different body |
| `state.invalid_transition` | 409 | No | Requested state change is not allowed |
| `provenance.immutable_after_capture` | 409 | No | Provenance links cannot be changed after capture |
| `webhooks.invalid_signature` | 400 | No | Webhook signature did not verify |

Test vectors for error responses: [`test-vectors/error-responses/`](../test-vectors/error-responses/)

## Retryable errors

Errors with `retryable: true` indicate a transient condition. Use exponential backoff with jitter before retrying. Do not retry errors with `retryable: false`.

## Idempotency

All mutating POST endpoints require an `Idempotency-Key` header:

```http
Idempotency-Key: 9e1b23b2-9ef3-4d8e-91a0-6e2c8a7f6f10
```

### Rules

- generate one key per logical write operation
- reuse a key **only** when safely retrying the exact same request
- reusing a key with a different payload returns `409 idempotency.key_reused_with_different_payload`
- keys are retained for 24 hours
- max key length: 128 characters, min: 8 characters

### Which endpoints require idempotency keys

Required:

- `POST /v1/payees`
- `POST /v1/transactions`
- `POST /v1/settlements`
- `POST /v1/refunds`

Recommended:

- `POST /v1/payment-intents`
- `POST /v1/invoices`

Constraints: [`constraints.json`](../constraints.json)

### Key generation

Use a UUID or a deterministic hash of the operation inputs:

```ts
import { randomUUID } from "crypto";
const idempotencyKey = randomUUID();
```

```python
import uuid
idempotency_key = str(uuid.uuid4())
```

### Test vectors

Idempotency behavior test vectors:

- [`test-vectors/idempotency/`](../test-vectors/idempotency/)

Includes:

- `replay-same-key-same-payload.json` — expect same response, no duplicate
- `replay-same-key-different-payload.json` — expect 409 conflict

## Webhook idempotency

Webhook events may be delivered more than once. Always:

1. persist the event `id` before processing
2. check whether the event ID has already been handled
3. skip processing if it has been seen before
4. return `200` regardless

## Related

- [Webhooks](./webhooks.md)
- [Authentication](./authentication.md)
- [Test vectors](../test-vectors/)
