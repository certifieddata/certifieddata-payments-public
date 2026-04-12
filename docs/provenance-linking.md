# Provenance Linking

Provenance linking is CDP's core differentiator. Every transaction can carry verifiable references to the AI artifacts, certificates, decisions, datasets, models, and outputs it funds.

## What provenance links are

A `ProvenanceLinkSet` is a structured object attached to a transaction. It records what was purchased and what was in force at the time of purchase.

This makes it possible to verify:

- what artifact or service was bought
- what certificate or attestation applied
- what decision record or policy reference was attached
- how settlement and refund history evolved after purchase

## Canonical schema

[`schemas/resources/provenance-link-set.schema.json`](../schemas/resources/provenance-link-set.schema.json)

## Supported link fields

| Field | Type | Description |
|---|---|---|
| `artifact_id` | string | The artifact being purchased or funded |
| `certificate_id` | string | Certificate or attestation in force at time of purchase |
| `decision_record_id` | string | Decision record or approval that authorized the transaction |
| `dataset_id` | string | Dataset linked to this commercial event |
| `model_id` | string | Model artifact referenced |
| `output_id` | string | Model output or inference result |
| `receipt_hash` | string | SHA-256 digest of the canonical payment receipt payload |
| `external_reference` | string | Opaque external reference (max 128 chars) |
| `provenance_metadata` | object | Namespaced key-value pairs (max 20 keys) |

## Provenance metadata namespacing

Keys in `provenance_metadata` must be namespaced:

- `cdp:` — CertifiedData internal references
- `partner:` — partner or integration system references
- `ext:` — external system references

Examples:

```json
{
  "cdp:workflow_id": "wf_2026_04_06_001",
  "cdp:source_system": "certifieddata-platform",
  "cdp:policy_id": "pol_research_v2",
  "partner:invoice_ref": "INV-44821",
  "ext:erp_order_id": "ERP-56789"
}
```

Constraints:

- max 20 keys per transaction
- max 512 characters per value
- keys must follow `{namespace}:{key}` format

Full namespace registry: [`schemas/provenance/recommended-metadata-keys.json`](../schemas/provenance/recommended-metadata-keys.json)

## Example: full provenance link set

```json
{
  "artifact_id": "art_01HXZ7Z8R2QQSN5B3T5VQ4D1WA",
  "certificate_id": "cert_01HXZ803C0R6V4K4P9HWB6J5N6",
  "decision_record_id": "dec_01HXZ80MCP6KNB8M3D0W1MSZV9",
  "dataset_id": "ds_01HXZ811N6C84YFJ4S2P7A5R1K",
  "receipt_hash": "sha256:3a6e0f8ed8c1f9d6f4d5b2a0cc6f12f876afc8b64c50d8b4c2c6aef6bd2b21f0",
  "external_reference": "partner:invoice-44821",
  "provenance_metadata": {
    "cdp:source_system": "partner_portal",
    "cdp:workflow_id": "wf_2026_04_06_001",
    "partner:invoice_ref": "INV-44821"
  }
}
```

## Mutability rules

Provenance links are **immutable after the transaction reaches `captured` status**.

Allowed before capture: `created`, `submitted`
Locked at and after: `captured`, `succeeded`, `failed`, `canceled`

If you attempt to attach links after capture, the API returns:

```json
{ "code": "provenance.immutable_after_capture", "http_status": 409 }
```

Mutability rules: [`schemas/mutability-map.json`](../schemas/mutability-map.json)

## Where provenance appears

Provenance links are embedded in:

- transaction responses
- all transaction lifecycle events
- settlement records
- receipt objects

## Attachment rules

Full attachment rules: [`schemas/provenance/provenance-attachment-rules.json`](../schemas/provenance/provenance-attachment-rules.json)

## Test vectors

Provenance test vectors (valid and invalid scenarios):

- [`test-vectors/provenance/`](../test-vectors/provenance/)

## Related

- [Transactions](./transactions.md)
- [Receipts](./receipts.md)
- [Errors and idempotency](./errors-and-idempotency.md)
