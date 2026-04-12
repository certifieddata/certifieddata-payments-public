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
    "receipt_id": "rcpt_...",
    "schema_version": "payment_receipt.v1",
    "sha256_hash": "sha256:...",
    "ed25519_sig": "base64...",
    "decision_record_id": "dec_...",
    "policy_id": "pol_...",
    "agent_id": "agt_...",
    "timestamp": "2026-04-06T18:42:11Z",
    "created_at": "2026-04-06T18:42:11Z"
  }
}
```

3. The `receipt_hash` can be attached as a provenance link to prove a specific payment receipt was associated with a transaction.

## Receipt fields

| Field | Description |
|-------|-------------|
| `receipt_id` | Receipt ID (`rcpt_` prefix) |
| `schema_version` | Always `"payment_receipt.v1"` |
| `sha256_hash` | SHA-256 digest of the canonical receipt payload (`sha256:<64 hex>`) |
| `ed25519_sig` | Base64-encoded Ed25519 signature over the canonical payload |
| `signing_key_id` | Key ID used; resolves in `/.well-known/certifieddata.json` |
| `decision_record_id` | Decision record bound to this payment via attach-links |
| `policy_id` | Payment policy that authorized this transaction |
| `agent_id` | Agent that initiated this transaction |
| `timestamp` | RFC 3339 timestamp of receipt issuance |
| `created_at` | Same as `timestamp`; included for API consistency |

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
