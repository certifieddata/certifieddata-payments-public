# API Resources

CDP uses a compact set of commercial and provenance-aware resource types.

## Resource index

| Resource | ID prefix | Schema | State machine |
|---|---|---|---|
| Payee | `py_` | `schemas/resources/payee.schema.json` | — |
| PayeeAlias | `pya_` | `schemas/resources/payee-alias.schema.json` | — |
| PayoutDestination | `pydst_` | `schemas/resources/payout-destination.schema.json` | `schemas/state-machines/payout-destination.state-machine.json` |
| Customer | `cus_` | `schemas/resources/customer.schema.json` | — |
| Invoice | `inv_` | `schemas/resources/invoice.schema.json` | `schemas/state-machines/invoice.state-machine.json` |
| PaymentIntent | `pi_` | `schemas/resources/payment-intent.schema.json` | `schemas/state-machines/payment-intent.state-machine.json` |
| Transaction | `tx_` | `schemas/resources/transaction.schema.json` | `schemas/state-machines/transaction.state-machine.json` |
| Receipt | `rcpt_` | `schemas/resources/receipt.schema.json` | — |
| Settlement | `stl_` | `schemas/resources/settlement.schema.json` | `schemas/state-machines/settlement.state-machine.json` |
| Refund | `rf_` | `schemas/resources/refund.schema.json` | `schemas/state-machines/refund.state-machine.json` |
| Event | `evt_` | `schemas/resources/event.schema.json` | — |
| WebhookEndpoint | `wh_` | `schemas/resources/webhook-endpoint.schema.json` | — |
| IdempotencyRecord | `idem_` | `schemas/resources/idempotency-record.schema.json` | — |
| ProvenanceLinkSet | — | `schemas/resources/provenance-link-set.schema.json` | — |

## Typical relationships

- a customer initiates a payment intent or transaction
- a transaction may reference an invoice or payment intent
- a transaction carries a provenance link set (artifact, certificate, decision)
- a receipt is issued when a transaction is captured
- a settlement routes funds to a payee via a payout destination
- a refund references the original transaction
- lifecycle changes emit events delivered to webhook endpoints

## Payment rails

| Rail | Description |
|---|---|
| `stripe` | Stripe card and bank payment |
| `usdc_base` | USDC on Base (L2) |
| `usdc_ethereum` | USDC on Ethereum mainnet |
| `eth_ethereum` | ETH on Ethereum mainnet |

Rail registry: [`schemas/enums/payment-rails.json`](../schemas/enums/payment-rails.json)

## Transaction lifecycle

```
created → submitted → captured → succeeded
                              ↘ failed
       ↘ canceled
```

Full state machine: [`schemas/state-machines/transaction.state-machine.json`](../schemas/state-machines/transaction.state-machine.json)

Status registry: [`schemas/enums/transaction-statuses.json`](../schemas/enums/transaction-statuses.json)

## Receipt

A receipt is a cryptographic proof artifact issued when a transaction is captured. It includes:

- receipt ID (`rcpt_` prefix)
- schema version (`payment_receipt.v1`)
- receipt hash (SHA-256 of canonical receipt payload)
- issued timestamp

Receipts are **immutable after issuance**. See [`schemas/resources/receipt.schema.json`](../schemas/resources/receipt.schema.json).

## Mutability

Different fields on different resources have different mutability rules after key lifecycle events.

Canonical mutability map: [`schemas/mutability-map.json`](../schemas/mutability-map.json)

## Source of truth

Field-level definitions live in the JSON Schemas:

- [`schemas/resources/`](../schemas/resources/)
- [`schemas/common/`](../schemas/common/)
- [`openapi/certifieddata-agent-commerce-v1.openapi.yaml`](../openapi/certifieddata-agent-commerce-v1.openapi.yaml)

## Related

- [Provenance linking](./provenance-linking.md)
- [Receipts](./receipts.md)
- [Transactions](./transactions.md)
- [Webhooks](./webhooks.md)
