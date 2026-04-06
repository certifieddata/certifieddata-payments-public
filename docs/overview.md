# CertifiedData Payments — Overview

CertifiedData Payments (CDP) is a provenance-aware commerce and settlement layer for the CertifiedData ecosystem. It enables payments that carry verifiable links to the AI artifacts, certificates, datasets, decisions, and models they fund.

## Machine-readable-first

This documentation is a supplement to the machine-readable contract. For authoritative definitions, start with:

- [`api-manifest.json`](../api-manifest.json) — root discovery entrypoint
- [`openapi/certifieddata-payments-v1.openapi.yaml`](../openapi/certifieddata-payments-v1.openapi.yaml) — REST contract
- [`schemas/resources/`](../schemas/resources/) — canonical resource definitions

## Core resources

| Resource | Prefix | Description |
|---|---|---|
| Payee | `py_` | A vendor or merchant who receives settlements |
| PayeeAlias | `pya_` | External-system reference mapped to a Payee |
| PayoutDestination | `pydst_` | A verified payout destination for a Payee |
| Customer | `cus_` | A payer who funds PaymentIntents |
| Invoice | `inv_` | A request for payment |
| PaymentIntent | `pi_` | Payer-facing collection intent |
| Transaction | `tx_` | Immutable ledger record created at capture |
| Settlement | `stl_` | Payout batch from CDP to a Payee |
| Refund | `rf_` | Full or partial reversal of a Transaction |

## Core differentiator: Provenance linking

Transactions carry provenance links to the artifacts and decisions they fund:

```
artifact_id, certificate_id, decision_id, dataset_id, model_id,
output_id, receipt_hash, external_reference, provenance_metadata
```

Provenance links are mutable until a transaction is captured. After capture, they are immutable.

## PaymentIntent vs Transaction

These are distinct concepts:

- **PaymentIntent** — payer-facing collection intent. Can be confirmed or canceled before capture.
- **Transaction** — immutable ledger record created when a PaymentIntent is captured. Cannot be modified after creation, only annotated.

## Environments

- `sandbox` — `cdp_test_...` API keys, `livemode: false`
- `live` — `cdp_live_...` API keys, `livemode: true`

IDs and credentials are environment-scoped and non-portable.

## Next steps

- [Quickstart](./quickstart.md)
- [Authentication](./authentication.md)
- [Provenance Linking](./provenance-linking.md)
