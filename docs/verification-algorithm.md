# Receipt Verification Algorithm

This document specifies the exact algorithm used to produce and verify receipt hashes.
Third-party verifiers must follow this specification to independently reproduce the
SHA-256 hash stored in every receipt.

## Why this matters

Every CertifiedData Agent Commerce receipt includes a `sha256_hash` field of the form
`sha256:<64 hex chars>`. This hash is computed from the canonical receipt payload and
signed with Ed25519. The hash is the tamper-detection mechanism: any modification to
the receipt payload produces a different hash that will not match the stored value or
the signature.

The verification endpoint (`GET /api/payments/verify/:receipt_id`) recomputes the hash
server-side and returns `hashValid: true` only when the recomputed hash equals the stored
hash. To independently verify receipts *without* calling the platform, you must reproduce
the hash using the algorithm below.

---

## Step 1 — Obtain the canonical receipt payload

The receipt payload is a JSON object returned in the `receipt` field of the capture
response and also available via `GET /api/payments/verify/:receipt_id` under the `receipt`
key.

The payload contains the fields defined in `schemas/resources/receipt.schema.json`.

**Important:** The hash is computed over the *base* receipt payload fields only.
The following fields are appended to the capture response *after* hashing and must
be excluded when reproducing the hash:

- `sha256_hash` — the hash itself
- `ed25519_sig` — the signature over the payload

All other fields present in the `receipt` object (including `null` values) are included
in the canonical payload.

---

## Step 2 — Canonical JSON serialization

Serialize the payload using **stable JSON serialization**:

1. Sort all object keys lexicographically (ASCII order), recursively
2. Exclude any key whose value is `undefined` (keys with `null` values are included as `null`)
3. No whitespace — no spaces or newlines between tokens
4. Encode as UTF-8 bytes

This is equivalent to:

- **JavaScript/TypeScript:** `require('json-stable-stringify')(payload)` encoded as UTF-8
- **Python:** `json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')`
- **Go:** Sort map keys before marshalling; use `json.Marshal` with a custom encoder

### Example

Given this payload:

```json
{
  "schema_version": "payment_receipt.v1",
  "receipt_id": "abc123",
  "amount": 2500,
  "currency": "usd",
  "decision_record_id": null
}
```

The canonical serialization is the UTF-8 bytes of:

```
{"amount":2500,"currency":"usd","decision_record_id":null,"receipt_id":"abc123","schema_version":"payment_receipt.v1"}
```

Note that keys are sorted alphabetically (`amount` before `currency` before `decision_record_id`, etc.)
and `null` is preserved (not dropped).

---

## Step 3 — SHA-256 hash

Compute the SHA-256 hash of the canonical UTF-8 bytes from Step 2.

Express the result as lowercase hexadecimal and prepend `sha256:`:

```
sha256:<64 lowercase hex chars>
```

This value must match the `sha256_hash` field in the receipt.

### Code examples

**Python:**
```python
import hashlib, json

def canonical_bytes(payload: dict) -> bytes:
    return json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')

def sha256_hash(payload: dict) -> str:
    return 'sha256:' + hashlib.sha256(canonical_bytes(payload)).hexdigest()
```

**JavaScript/TypeScript:**
```ts
import stableStringify from 'json-stable-stringify';
import { createHash } from 'node:crypto';

function sha256Hash(payload: Record<string, unknown>): string {
  const bytes = Buffer.from(stableStringify(payload)!, 'utf-8');
  return 'sha256:' + createHash('sha256').update(bytes).digest('hex');
}
```

---

## Step 4 — Ed25519 signature verification (optional)

The receipt is also signed with Ed25519. To verify the signature:

1. Obtain the canonical bytes from Step 2
2. Decode the `ed25519_sig` field from base64 (standard base64, not URL-safe)
3. Obtain the platform public key from `GET /.well-known/certifieddata.json` using
   the `signingKeyId` returned by the verify endpoint
4. Verify the Ed25519 signature over the canonical bytes using the public key

The platform verify endpoint (`GET /api/payments/verify/:receipt_id`) performs both hash
and signature verification and returns a structured result:

```json
{
  "valid": true,
  "hashValid": true,
  "signatureValid": true,
  "signingKeyId": "cd_root_2026",
  "signatureAlg": "Ed25519",
  "storedReceiptHash": "sha256:...",
  "recomputedReceiptHash": "sha256:..."
}
```

`valid` is `true` only if both `hashValid` and `signatureValid` are `true`.

> **Note on casing:** The verify response uses **camelCase** field names (`hashValid`, `signatureValid`,
> `signingKeyId`, `storedReceiptHash`, `recomputedReceiptHash`). The receipt object itself uses
> **snake_case** (`sha256_hash`, `ed25519_sig`, `signing_key_id`). Do not mix the two when
> implementing a verifier.

---

## Worked example

### Canonical payload (redacted for brevity)

```json
{
  "amount": 2500,
  "authorization_id": "a1b2c3d4-...",
  "currency": "usd",
  "decision_record_id": "dec_agent_demo_2026",
  "policy_id": "pol_01HZX8E77KN1KZ9M2G5D5Q4N4V",
  "rail": "stripe",
  "receipt_id": "rcpt_01HZX8M9QRH7Y8B4M2S2W6D1J5",
  "schema_version": "payment_receipt.v1",
  "status": "submitted",
  "timestamp": "2026-04-06T18:42:11.000Z",
  "transaction_id": "tx_01HZX8KHJNR4D42R6G4W4Q0Y0V"
}
```

### Expected hash

```
sha256:3a6e0f8ed8c1f9d6f4d5b2a0cc6f12f876afc8b64c50d8b4c2c6aef6bd2b21f0
```

(Illustrative — the real hash depends on all field values.)

---

## Notes on key rotation

The platform supports signing key rotation. Every receipt stores the `signingKeyId` used
at issuance. Old receipts remain verifiable as long as the corresponding public key exists
in the key registry, regardless of the current active private key.

Key rotation does not invalidate previously issued receipts.

---

## Testing your verifier

Use the mock server (`examples/claude-demo/mock_server.py`) to generate receipts locally.
The mock server uses the same canonical JSON algorithm as the production platform, so
receipts generated by the mock will pass hash verification using this algorithm.

Note: mock server signatures use an ephemeral key generated at startup. They are not
verifiable against the real platform's key registry.
