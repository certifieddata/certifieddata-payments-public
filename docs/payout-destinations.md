# Payout Destinations

A **PayoutDestination** (`pydst_` prefix) defines where funds are sent for a given payee. Each destination is linked to a payment rail and goes through a verification lifecycle.

## Machine-readable references

- Schema: [schemas/resources/payout-destination.schema.json](../schemas/resources/payout-destination.schema.json)
- State machine: [schemas/state-machines/payout-destination.state-machine.json](../schemas/state-machines/payout-destination.state-machine.json)
- Example: [examples/json/payout-destination.create.request.json](../examples/json/payout-destination.create.request.json)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/payees/{payee_id}/payout-destinations` | Create a payout destination |
| `GET` | `/v1/payees/{payee_id}/payout-destinations` | List payout destinations for a payee |
| `PATCH` | `/v1/payout-destinations/{destination_id}` | Update a payout destination |

## Lifecycle

```
pending_verification → active
                     ↘ rejected
active → inactive
```

## TypeScript SDK

```typescript
const dest = await client.payees.createPayoutDestination(
  payeeId,
  { rail_type: "stripe", is_default: true, processor_ref: "acct_1QExample" },
  { idempotencyKey: "dest-001" }
);
```

## Notes

- `processor_ref` is the public-safe processor account reference (never a secret key)
- `status` and `processor_ref` are server-managed after creation
- Mutability: `is_default` is mutable; `processor_ref` and `status` are immutable after creation. See [schemas/mutability-map.json](../schemas/mutability-map.json).
