# TypeScript SDK

The `@certifieddata/payments` package is the official TypeScript/Node.js SDK for CertifiedData Payments.

## Installation

```bash
npm install @certifieddata/payments
# or
pnpm add @certifieddata/payments
```

**Requirements:** Node.js ≥ 18 (uses native `fetch`), ESM.

## Quick start

```typescript
import { CertifiedDataPaymentsClient } from "@certifieddata/payments";

const client = new CertifiedDataPaymentsClient({
  apiKey: process.env.CDP_API_KEY!,
  // baseUrl: "http://localhost:3456",  // point to mock server for local dev
});

const payee = await client.payees.create(
  { entity_type: "company", legal_name: "Acme Corp" },
  { idempotencyKey: "create-payee-acme-001" }
);
```

## Client options

| Option | Type | Description |
|--------|------|-------------|
| `apiKey` | `string` | Required. Use `cdp_test_` for sandbox, `cdp_live_` for production. |
| `baseUrl` | `string` | Defaults to `https://api.certifieddata.io`. Override for mock server. |
| `apiVersion` | `string` | Defaults to `2025-01-01`. |
| `idempotencyKey` | `string` | Attach a key to every mutating request on this instance. |

## Idempotency

Pass per-request:
```typescript
await client.transactions.create(params, { idempotencyKey: "tx-001" });
```

Or use a scoped client:
```typescript
const idempotent = client.withIdempotencyKey("my-operation-001");
await idempotent.transactions.create(params);
```

## Webhook verification

```typescript
const isValid = await client.verifyWebhookSignature(
  rawBody,
  req.headers["cdp-signature"],
  req.headers["cdp-timestamp"],
  process.env.CDP_WEBHOOK_SECRET!
);
```

Or use the standalone function:
```typescript
import { verifyWebhookSignature } from "@certifieddata/payments";
```

## Pagination

```typescript
import { listAll } from "@certifieddata/payments";

const allPayees = await listAll((params) => client.payees.list(params));
```

## Resources

| Client property | Endpoints |
|-----------------|-----------|
| `client.payees` | Payees, aliases, payout destinations |
| `client.paymentIntents` | Payment intents |
| `client.transactions` | Transactions, attach-links, capture |
| `client.settlements` | Settlements, submit, cancel |
| `client.refunds` | Refunds |
| `client.events` | Events |
| `client.webhooks` | Webhook endpoints, signature verification |
| `client.capabilities` | Capabilities, health, version |

## Error handling

```typescript
import { CDPError, CDPConflictError } from "@certifieddata/payments";

try {
  await client.transactions.attachLinks(txId, links);
} catch (err) {
  if (err instanceof CDPConflictError && err.code === "provenance.immutable_after_capture") {
    // Transaction already captured — provenance is locked
  }
}
```

## Source

[packages/typescript-sdk/](../packages/typescript-sdk/)
