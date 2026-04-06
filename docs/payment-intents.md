# Payment Intents

A **PaymentIntent** (`pi_` prefix) represents the intent to collect funds from a customer for a specific amount on a specific payment rail.

> **PaymentIntent vs Transaction:** A PaymentIntent is the payer-facing collection intent. When a PaymentIntent is captured, an immutable **Transaction** ledger record is created. See [transactions.md](transactions.md) for the post-capture record.

## Machine-readable references

- Schema: [schemas/resources/payment-intent.schema.json](../schemas/resources/payment-intent.schema.json)
- State machine: [schemas/state-machines/payment-intent.state-machine.json](../schemas/state-machines/payment-intent.state-machine.json)
- Example: [examples/json/payment-intent.create.request.json](../examples/json/payment-intent.create.request.json)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/payment-intents` | Create a payment intent |
| `GET` | `/v1/payment-intents/{id}` | Retrieve a payment intent |
| `GET` | `/v1/payment-intents` | List payment intents |
| `POST` | `/v1/payment-intents/{id}/confirm` | Confirm a payment intent |
| `POST` | `/v1/payment-intents/{id}/cancel` | Cancel a payment intent |

## Lifecycle

```
created → confirmed → processing → succeeded
                ↘               ↘ failed
                 → canceled
```

See the canonical lifecycle in [schemas/state-machines/payment-intent.state-machine.json](../schemas/state-machines/payment-intent.state-machine.json).

## TypeScript SDK

```typescript
const intent = await client.paymentIntents.create(
  { amount: 4900, currency: "USD", rail: "stripe" },
  { idempotencyKey: "intent-001" }
);
await client.paymentIntents.confirm(intent.id, { idempotencyKey: `confirm-${intent.id}` });
```

## Idempotency

`POST /v1/payment-intents` and confirm/cancel actions support idempotency keys. See [idempotency.md](idempotency.md).
