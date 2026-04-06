# Idempotency

All mutating POST endpoints require an `Idempotency-Key` header.

```
Idempotency-Key: your-unique-key-here
```

## Rules

- Key max length: 128 characters, min length: 8 characters
- Use a UUID or similarly random value per unique request intent
- Replay the **exact same** payload with the same key to get the same result
- Reusing a key with a **different payload** returns HTTP 409 (`idempotency.key_reused_with_different_payload`)
- Records are retained for 24 hours

## Behavior

| Scenario | Result |
|---|---|
| First request | Creates resource, caches response |
| Replay with same key + same payload | Returns cached response (same resource ID) |
| Replay with same key + different payload | HTTP 409 |
| New key | Creates new resource |

## Machine-readable limits

See [`constraints.json`](../constraints.json) for canonical idempotency limits.

## Test vectors

See [`test-vectors/idempotency/`](../test-vectors/idempotency/) for machine-verifiable test cases.
