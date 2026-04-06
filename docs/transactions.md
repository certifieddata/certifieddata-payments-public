# Transactions

A Transaction is an immutable ledger record created when a PaymentIntent is captured.

**Key distinction:** A Transaction is NOT the same as a PaymentIntent. The PaymentIntent is the payer-facing collection intent; the Transaction is the post-capture immutable record.

## Lifecycle

See [`schemas/state-machines/transaction.state-machine.json`](../schemas/state-machines/transaction.state-machine.json):

`created → submitted → captured → succeeded | failed`
`created → canceled`
`submitted → canceled`

## Provenance links

Provenance links can be attached before capture. They are immutable after `captured` status.

## Receipt

A receipt sub-object is embedded on the transaction when `status = succeeded`.

```json
{
  "receipt": {
    "id": "rcpt_...",
    "schema_version": "payment_receipt.v1",
    "hash": "sha256:...",
    "created_at": "2026-04-06T18:42:11Z"
  }
}
```

## Canonical schema

[`schemas/resources/transaction.schema.json`](../schemas/resources/transaction.schema.json)

## Examples

- [`examples/json/transaction.create.request.json`](../examples/json/transaction.create.request.json)
- [`examples/json/transaction.with-full-provenance.response.json`](../examples/json/transaction.with-full-provenance.response.json)

## Endpoints

```
POST   /v1/transactions
GET    /v1/transactions/{id}
GET    /v1/transactions
POST   /v1/transactions/{id}/attach-links
POST   /v1/transactions/{id}/capture
POST   /v1/transactions/{id}/cancel
```
