# Receipts

A **Receipt** (`rcpt_` prefix) is an immutable signed artifact issued when a transaction is captured. Receipts prove that a payment occurred and link it to provenance data.

## Machine-readable references

- Schema: [schemas/resources/receipt.schema.json](../schemas/resources/receipt.schema.json)

## How receipts work

1. A transaction is captured (`POST /v1/transactions/{id}/capture`)
2. The platform issues a receipt and embeds it on the transaction response:

```json
{
  "id": "tx_...",
  "status": "captured",
  "receipt": {
    "id": "rcpt_...",
    "schema_version": "payment_receipt.v1",
    "hash": "sha256:...",
    "created_at": "2026-04-06T18:42:11Z"
  }
}
```

3. The `receipt_hash` can be attached as a provenance link to prove a specific payment receipt was associated with a transaction.

## Receipt fields

| Field | Description |
|-------|-------------|
| `id` | Receipt ID (`rcpt_` prefix) |
| `schema_version` | Always `"payment_receipt.v1"` |
| `hash` | SHA-256 digest of the canonical receipt payload |
| `created_at` | Timestamp of receipt issuance |

## Immutability

Receipts are immutable after issuance. See [schemas/mutability-map.json](../schemas/mutability-map.json).

## Provenance linking

The `receipt_hash` field in `ProvenanceLinkSet` allows you to reference a specific receipt:

```typescript
await client.transactions.attachLinks(txId, {
  receipt_hash: "sha256:...",
  certificate_id: "cert_...",
});
```

See [provenance-linking.md](provenance-linking.md).

## V1 endpoint

`GET /v1/receipts/{receipt_id}` — retrieve a standalone receipt by ID.

Receipts are also embedded on transaction responses when `status = captured` or `succeeded`.
