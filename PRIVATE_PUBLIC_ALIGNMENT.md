# CertifiedData Payments — Private to Public Alignment

## Purpose

Maps private platform concepts to public CertifiedData Payments contract concepts.

---

## Alignment principles

1. Public naming should remain stable and explicit.
2. Public schemas should align to private domain semantics where possible.
3. Private execution detail should not be surfaced directly.
4. Public enums should not exceed currently supported private capabilities.
5. Where the private platform has richer detail, the public contract exposes a safe abstraction.

---

## Canonical mappings

| Private concept | Public concept | Notes |
|---|---|---|
| payment rail enum | `PaymentRail` | Public values must align with supported private rails |
| payment transaction | `Transaction` | Clean contract abstraction, not raw internal ledger shape |
| payment receipt payload | `Receipt` sub-object on transaction | Align semantically, never leak private signing material |
| payment authorization | `PaymentIntent` lifecycle semantics | Expose only public lifecycle |
| merchant profile | `Payee` resource | Renamed; stripeAccountRef stays private |
| agent account | NOT exposed in V1 | Internal concept |
| policy evaluation result | public-safe outcome fields only | Do not expose rule reasoning internals |

---

## Supported public rails

- `stripe`, `usdc_base`, `usdc_ethereum`, `eth_ethereum`

Do not invent additional rails unless explicitly approved.

---

## Public status alignment

**Transaction:** created, submitted, captured, succeeded, failed, canceled

**PaymentIntent:** created, confirmed, processing, succeeded, failed, canceled

**Settlement:** draft, submitted, processing, succeeded, failed, canceled

**Refund:** created, processing, succeeded, failed

**PayoutDestination:** pending_verification, active, rejected, inactive

Do not add statuses not supported by the public lifecycle model.

---

## Receipt alignment

Public receipt shape supports:
- receipt identifier (`rcpt_` prefix)
- receipt version (`payment_receipt.v1`)
- transaction identifier
- rail, amount, currency
- created timestamp
- SHA-256 hash of canonical receipt payload
- signature presence indicator (not the key)

Does not expose:
- private signing keys or key PEM
- internal signing pipeline identifiers

---

## Provenance alignment

Public fields: artifact_id, certificate_id, decision_id, dataset_id, model_id, output_id, receipt_hash, external_reference, provenance_metadata

These map to real private platform trust/decision identifiers. The public contract remains a stable interface.

---

## Fields that MUST stay private

- `stripeAccountRef`
- raw crypto wallet addresses as payout destinations
- `privateKey` / signing key PEM
- `STRIPE_WEBHOOK_SECRET`
- `requireHumanReviewOverCents` exact threshold values
- Policy rule internals (allowedMerchants list, dailyLimitCents)
- `externalPaymentIntentId` (raw Stripe PI ID) — use abstracted `processor_reference`

---

## Event alignment

Public events correspond to meaningful lifecycle transitions in the private platform.

Examples: payee.created, payment_intent.confirmed, transaction.captured, settlement.succeeded, refund.failed

The public event envelope remains stable even if private event delivery or internal services evolve.

---

## Environment alignment

Public environments: sandbox, live

API keys, webhook delivery, and mock server behavior must align to this model. IDs and secrets are environment-scoped and non-portable.

---

## If there is uncertainty

When a private concept is richer than the public contract:
- preserve public stability
- expose the minimal useful abstraction
- do not leak internals
- note the alignment in comments/docs if needed
