# Refunds

A **Refund** (`rf_` prefix) initiates a reversal of a captured transaction back to the original payer.

## Machine-readable references

- Schema: [schemas/resources/refund.schema.json](../schemas/resources/refund.schema.json)
- State machine: [schemas/state-machines/refund.state-machine.json](../schemas/state-machines/refund.state-machine.json)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/refunds` | Create a refund |
| `GET` | `/v1/refunds/{id}` | Retrieve a refund |
| `GET` | `/v1/refunds` | List refunds |

## Lifecycle

```
created → processing → succeeded
                     ↘ failed
```

## Reason codes

| Reason | Description |
|--------|-------------|
| `duplicate` | Duplicate charge |
| `fraudulent` | Fraudulent charge |
| `customer_request` | Customer requested refund |
| `partial_adjustment` | Partial amount adjustment |

## TypeScript SDK

```typescript
const refund = await client.refunds.create(
  {
    transaction_id: "tx_...",
    amount: 4900,
    reason: "customer_request",
  },
  { idempotencyKey: "refund-001" }
);
```

## Idempotency

`POST /v1/refunds` requires an idempotency key. See [idempotency.md](idempotency.md).
