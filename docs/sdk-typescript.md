# TypeScript SDK

The `@certifieddata/payments` package is the official TypeScript/Node.js SDK for CertifiedData Payments.

**Repo path:** [`packages/typescript-sdk/`](../packages/typescript-sdk/)

## Install

```bash
pnpm add @certifieddata/payments
```

## Client setup

```ts
import { CertifiedDataPaymentsClient } from "@certifieddata/payments";

const client = new CertifiedDataPaymentsClient({
  apiKey: process.env.CDP_API_KEY!,
  apiVersion: "2025-01-01",
});
```

### Sandbox / mock server

```ts
const client = new CertifiedDataPaymentsClient({
  apiKey: "cdp_test_your_key",
  apiVersion: "2025-01-01",
  baseUrl: "http://localhost:3456",
});
```

## Idempotent requests

Scope idempotency to a specific write operation:

```ts
const idempotent = client.withIdempotencyKey("my-unique-key-001");

const payee = await idempotent.payees.create({
  entity_type: "company",
  legal_name: "Atlas Synthetic Labs, Inc.",
  email: "payments@atlas-synthetic.example",
});
```

## Create a transaction

```ts
const tx = await client.transactions.create({
  payment_intent_id: "pi_01HZX8H75Z6X8C5X7JQY6B4M2N",
  payee_id: "py_01HZX8E77KN1KZ9M2G5D5Q4N4V",
  amount: 4900,
  currency: "usd",
  rail: "stripe",
  description: "Certified artifact purchase",
});
```

## Attach provenance links

Provenance links are immutable after capture. Attach before confirming payment.

```ts
await client.transactions.attachLinks(tx.id, {
  artifact_id: "art_01HXZ7Z8R2QQSN5B3T5VQ4D1WA",
  certificate_id: "cert_01HXZ803C0R6V4K4P9HWB6J5N6",
  decision_id: "dec_01HXZ80MCP6KNB8M3D0W1MSZV9",
  provenance_metadata: {
    "cdp:workflow_id": "wf_123",
    "cdp:source_system": "certifieddata-platform",
  },
});
```

## Verify a webhook signature

```ts
const isValid = await client.webhooks.verifySignature(
  rawBody,
  signatureHeader,  // CDP-Signature header value
  timestampHeader,  // CDP-Timestamp header value
  webhookSecret,
);
```

Validate your implementation using the test vectors in [`test-vectors/webhook-signature/`](../test-vectors/webhook-signature/).

## Pagination

All list endpoints return cursor-paginated results:

```ts
const first = await client.transactions.list({ limit: 20 });

if (first.has_more) {
  const next = await client.transactions.list({
    limit: 20,
    starting_after: first.data[first.data.length - 1].id,
  });
}
```

## Error handling

```ts
import { CdpApiError } from "@certifieddata/payments";

try {
  await client.transactions.create({ ... });
} catch (err) {
  if (err instanceof CdpApiError) {
    console.error(err.code, err.httpStatus, err.message);
  }
}
```

## Best use cases

- server-side platform billing flows
- webhook consumers
- internal reconciliation tooling
- certified artifact purchase flows

## Related

- [Python SDK](./sdk-python.md)
- [Authentication](./authentication.md)
- [Provenance links](./provenance-links.md)
- [Sandbox and mock server](./sandbox-and-mock-server.md)
