# Webhooks

CDP delivers signed events to your registered webhook endpoints.

## Registration

```
POST /v1/webhook-endpoints
{
  "url": "https://your-domain.example/webhooks/cdp",
  "enabled_events": ["transaction.captured", "settlement.succeeded"],
  "description": "Production webhook"
}
```

Use `["*"]` for all events.

## Signature verification

All requests include:
- `CDP-Signature: t={timestamp},v1={hmac_sha256}`
- `CDP-Timestamp: {unix_timestamp}`
- `CDP-Event-Id: {event_id}`
- `CDP-Api-Version: {api_version}`

### Signing algorithm

1. Construct the signed payload: `{timestamp}.{raw_body}`
2. Compute HMAC-SHA256 with your webhook secret as the key
3. Compare with the `v1` value in `CDP-Signature`
4. Reject if the timestamp is more than 300 seconds from now

### TypeScript example

```typescript
import { verifyWebhookSignature } from "@certifieddata/payments/webhooks";

const isValid = verifyWebhookSignature({
  payload: rawBody,           // string — the raw request body
  signature: sigHeader,       // CDP-Signature header value
  timestamp: timestampHeader, // CDP-Timestamp header value
  secret: webhookSecret,      // your endpoint's secret
});
```

### Python example

```python
from certifieddata_payments import verify_webhook_signature

is_valid = verify_webhook_signature(
    payload=raw_body,
    signature=request.headers["CDP-Signature"],
    timestamp=request.headers["CDP-Timestamp"],
    secret=webhook_secret,
)
```

## Machine-readable constraints

- Signature algorithm: `hmac-sha256`
- Timestamp tolerance: 300 seconds
- See [`constraints.json`](../constraints.json) for all webhook limits

## Test vectors

See [`test-vectors/webhook-signature/`](../test-vectors/webhook-signature/) for valid and invalid signature test cases.

## Event envelope

All events share the same envelope. See [`schemas/resources/event.schema.json`](../schemas/resources/event.schema.json) and [`examples/json/event.transaction.captured.json`](../examples/json/event.transaction.captured.json).
