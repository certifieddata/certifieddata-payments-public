# Quickstart

## 1. Install the SDK

```bash
# TypeScript
pnpm add @certifieddata/payments

# Python
pip install certifieddata-payments
```

## 2. Start the mock server (local development)

```bash
git clone https://github.com/certifieddata/certifieddata-payments-public.git
cd certifieddata-payments-public
pnpm install
pnpm mock
# Mock server running at http://localhost:3456
```

## 3. Create a Payee

```typescript
import { CertifiedDataPaymentsClient } from "@certifieddata/payments";

const client = new CertifiedDataPaymentsClient({
  apiKey: "cdp_test_...",
  baseUrl: "http://localhost:3456", // or https://api.certifieddata.io
});

const payee = await client.payees.create(
  {
    entity_type: "company",
    legal_name: "Atlas Synthetic Labs, Inc.",
    email: "payments@atlas-synthetic.example",
    default_payout_method: "stripe",
    metadata: { "cdp:source_system": "partner_portal" },
  },
  { idempotencyKey: "payee-atlas-001" }
);

console.log(payee.id); // py_test_0001
```

## 4. Create a Transaction with provenance links

```typescript
// Create payment intent
const intent = await client.paymentIntents.create(
  {
    customer_id: "cus_...",
    amount: 25000,
    currency: "USD",
    rail: "stripe",
    description: "Certified artifact purchase",
  },
  { idempotencyKey: "pi-certified-001" }
);

// Create transaction
const tx = await client.transactions.create(
  {
    payment_intent_id: intent.id,
    payee_id: payee.id,
    amount: 25000,
    currency: "USD",
    rail: "stripe",
  },
  { idempotencyKey: "tx-certified-001" }
);

// Attach provenance links (must be done before capture)
await client.transactions.attachLinks(tx.id, {
  artifact_id: "art_...",
  certificate_id: "cert_...",
  decision_id: "dec_...",
  provenance_metadata: {
    "cdp:workflow_id": "wf_123",
    "partner:invoice_ref": "INV-44821",
  },
});

// Capture
const captured = await client.transactions.capture(tx.id);
console.log(captured.receipt?.id); // rcpt_...
console.log(captured.receipt?.schema_version); // payment_receipt.v1
```

## 5. Verify webhook signatures

```typescript
import { verifyWebhookSignature } from "@certifieddata/payments/webhooks";

// In your webhook handler
const isValid = verifyWebhookSignature({
  payload: rawBody,
  signature: req.headers["cdp-signature"],
  timestamp: req.headers["cdp-timestamp"],
  secret: process.env.CDP_WEBHOOK_SECRET,
});

if (!isValid) {
  return res.status(400).json({ error: "Invalid signature" });
}
```

## Next steps

- [Authentication](./authentication.md)
- [Provenance Linking](./provenance-linking.md)
- [Webhooks](./webhooks.md)
- [Errors](./errors.md)
