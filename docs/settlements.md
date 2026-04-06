# Settlements

A **Settlement** (`stl_` prefix) groups captured transactions into a batch payout to a payee's payout destination.

## Machine-readable references

- Schema: [schemas/resources/settlement.schema.json](../schemas/resources/settlement.schema.json)
- State machine: [schemas/state-machines/settlement.state-machine.json](../schemas/state-machines/settlement.state-machine.json)
- Example: [examples/json/settlement.create.request.json](../examples/json/settlement.create.request.json)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/settlements` | Create a settlement |
| `GET` | `/v1/settlements/{id}` | Retrieve a settlement |
| `GET` | `/v1/settlements` | List settlements |
| `POST` | `/v1/settlements/{id}/submit` | Submit a settlement for processing |
| `POST` | `/v1/settlements/{id}/cancel` | Cancel a settlement (only while in `draft`) |

## Lifecycle

```
draft → submitted → processing → succeeded
                               ↘ failed
draft → canceled
```

## TypeScript SDK

```typescript
const settlement = await client.settlements.create(
  {
    payee_id: "py_...",
    amount: 25000,
    currency: "USD",
    transaction_ids: ["tx_..."],
  },
  { idempotencyKey: "settlement-batch-001" }
);
await client.settlements.submit(settlement.id, { idempotencyKey: `submit-${settlement.id}` });
```

## Idempotency

All state-changing operations support idempotency keys. See [idempotency.md](idempotency.md).
