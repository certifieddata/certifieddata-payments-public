# Provenance Linking

Provenance linking is CDP's core differentiator. Every transaction can carry verifiable references to the AI artifacts, certificates, decisions, datasets, models, and outputs it funds.

## ProvenanceLinkSet fields

| Field | Description |
|---|---|
| `artifact_id` | CertifiedData artifact identifier |
| `certificate_id` | CertifiedData certificate identifier |
| `decision_id` | DecisionLedger decision record identifier |
| `dataset_id` | Dataset identifier |
| `model_id` | Model identifier |
| `output_id` | AI output identifier |
| `receipt_hash` | SHA-256 digest of canonical receipt payload (`sha256:` prefix) |
| `external_reference` | Freeform external reference string (max 128 chars) |
| `provenance_metadata` | Namespaced key-value metadata |

See [`schemas/resources/provenance-link-set.schema.json`](../schemas/resources/provenance-link-set.schema.json) for the canonical schema.

## Attaching links

Use `POST /v1/transactions/{id}/attach-links`:

```typescript
await client.transactions.attachLinks("tx_...", {
  artifact_id: "art_...",
  certificate_id: "cert_...",
  decision_id: "dec_...",
  receipt_hash: "sha256:...",
  provenance_metadata: {
    "cdp:workflow_id": "wf_123",
    "partner:invoice_ref": "INV-44821",
  },
});
```

## Immutability rule

Provenance links are **mutable until** a transaction reaches `captured` status.

After `captured`, they are **immutable**. Attempting to modify links after capture returns HTTP 409 (`provenance.immutable_after_capture`).

See the state machine: [`schemas/state-machines/transaction.state-machine.json`](../schemas/state-machines/transaction.state-machine.json)

## Metadata namespacing

`provenance_metadata` keys must use a recognized namespace prefix:

| Namespace | Use |
|---|---|
| `cdp:` | CertifiedData internal references |
| `partner:` | Partner/integration references |
| `ext:` | External system references |

Max 20 keys, max 256 chars per value.

## receipt_hash vs artifact_hash

- `receipt_hash` — SHA-256 of the canonical payment receipt payload. Used to link a provenance set to a specific receipt.
- `artifact_hash` — a field on the receipt artifact proving what artifact was purchased. These are distinct concepts.

## Test vectors

See [`test-vectors/provenance/`](../test-vectors/provenance/) for verified attach-before-capture and attach-after-capture scenarios.
