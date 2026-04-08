# Payees

A **Payee** (`py_` prefix) represents a vendor, contractor, or AI service provider who receives payments via the CertifiedData Agent Commerce platform.

## Machine-readable references

- Schema: [schemas/resources/payee.schema.json](../schemas/resources/payee.schema.json)
- Example request: [examples/json/payee.create.request.json](../examples/json/payee.create.request.json)
- Example response: [examples/json/payee.create.response.json](../examples/json/payee.create.response.json)
- OpenAPI operations: [openapi/certifieddata-agent-commerce-v1.openapi.yaml](../openapi/certifieddata-agent-commerce-v1.openapi.yaml) → `/v1/payees`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/payees` | Create a payee |
| `GET` | `/v1/payees/{payee_id}` | Retrieve a payee |
| `GET` | `/v1/payees` | List payees |
| `PATCH` | `/v1/payees/{payee_id}` | Update a payee |
| `POST` | `/v1/payees/{payee_id}/aliases` | Create a payee alias |
| `GET` | `/v1/payees/{payee_id}/aliases` | List payee aliases |
| `POST` | `/v1/payees/{payee_id}/payout-destinations` | Create a payout destination |
| `GET` | `/v1/payees/{payee_id}/payout-destinations` | List payout destinations |

## TypeScript SDK

```typescript
const payee = await client.payees.create(
  {
    entity_type: "company",
    legal_name: "Atlas Synthetic Labs, Inc.",
    email: "payments@atlas-synthetic.example",
    default_payout_method: "stripe",
    metadata: { "partner:account_ref": "atlas-001" },
  },
  { idempotencyKey: "create-payee-atlas-001" }
);
```

## Python SDK

```python
payee = client.payees.create(
    entity_type="company",
    legal_name="Atlas Synthetic Labs, Inc.",
    email="payments@atlas-synthetic.example",
    idempotency_key="create-payee-atlas-001",
)
```

## Status lifecycle

| Status | Description |
|--------|-------------|
| `active` | Payee is active and can receive payments |
| `inactive` | Payee has been deactivated |

KYC status (`kyc_status`) is server-managed: `pending → verified | rejected`.

## Aliases

Aliases map external system references to CDP payee IDs, enabling lookups by your own reference IDs. Alias uniqueness is enforced on `(external_system, external_ref)`.

See: [schemas/resources/payee-alias.schema.json](../schemas/resources/payee-alias.schema.json)

## Payout destinations

Payout destinations define where funds are sent. Each destination is linked to a payment rail (`stripe`, `usdc_base`, etc.) and goes through a `pending_verification → active` lifecycle.

See: [schemas/resources/payout-destination.schema.json](../schemas/resources/payout-destination.schema.json)

## Idempotency

All `POST` and `PATCH` operations support idempotency. See [idempotency.md](idempotency.md).
