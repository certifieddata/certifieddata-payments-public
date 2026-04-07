# Webhooks

CDP delivers signed webhook events to your registered endpoints for transaction, settlement, and refund lifecycle changes.

## Event contract

Canonical event definitions:

- [`asyncapi/certifieddata-payments-events-v1.asyncapi.yaml`](../asyncapi/certifieddata-payments-events-v1.asyncapi.yaml)

## Typical events

- `payee.created`
- `transaction.created`
- `transaction.captured`
- `transaction.links_attached`
- `settlement.submitted`
- `settlement.succeeded`
- `settlement.failed`
- `refund.created`
- `refund.succeeded`
- `refund.failed`

Full event type registry: [`schemas/enums/event-types.json`](../schemas/enums/event-types.json)

## Signature verification

CDP signs every delivery with HMAC-SHA256.

**Signature header:** `CDP-Signature: t={timestamp},v1={hmac}`
**Timestamp header:** `CDP-Timestamp: {unix_timestamp}`
**Tolerance:** 300 seconds

Signed payload template:

```
{timestamp}.{raw_body}
```

Compute the expected signature:

```ts
const signed = `${timestamp}.${rawBody}`;
const expected = crypto
  .createHmac("sha256", webhookSecret)
  .update(signed)
  .digest("hex");
```

Compare `v1` from the header to the computed value. Reject if they differ or if the timestamp is outside the 300-second window.

### Test vectors

Machine-readable test vectors for signature verification:

- [`test-vectors/webhook-signature/`](../test-vectors/webhook-signature/)

Use these to validate your verification implementation before going live.

## Event envelope

Every event shares this shape:

```json
{
  "id": "evt_01HZX8M1W3D6K8Q4YJ6A1R9B2C",
  "event_type": "transaction.captured",
  "event_version": "1.0.0",
  "api_version": "2025-01-01",
  "occurred_at": "2026-04-06T18:42:11Z",
  "environment": "sandbox",
  "livemode": false,
  "resource_type": "transaction",
  "resource_id": "tx_01HZX8KHJNR4D42R6G4W4Q0Y0V",
  "data": { ... },
  "provenance": { ... },
  "request_context": { ... }
}
```

Field definitions: [`schemas/resources/event.schema.json`](../schemas/resources/event.schema.json)

## Receiver guidance

Webhook consumers must:

- verify the signature on every delivery
- persist the event `id` before processing — use it as an idempotency key
- respond with `200` promptly — move long-running work to an async queue
- handle retries gracefully — the same event may be delivered more than once
- reconcile event state against your own transaction records

## Operational guidance

- maintain separate webhook endpoints for sandbox and live
- log delivery attempts, event IDs, and processing outcomes
- alert on unexpected `5xx` delivery failures from CDP
- reconcile webhook events against transaction state in your own DB

## Related

- [Idempotency](./errors-and-idempotency.md)
- [Errors](./errors-and-idempotency.md)
- [Test vectors](../test-vectors/)
