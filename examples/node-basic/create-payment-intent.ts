/**
 * Example: Create and confirm a payment intent.
 *
 * Run against mock server:
 *   npx tsx examples/node-basic/create-payment-intent.ts
 */

import { CertifiedDataPaymentsClient } from "@certifieddata/payments";

const client = new CertifiedDataPaymentsClient({
  apiKey: "cdp_test_example_key",
  baseUrl: "http://localhost:3456",
});

async function main() {
  // 1. Create a payment intent
  const intent = await client.paymentIntents.create(
    {
      amount: 25000, // $250.00 in cents
      currency: "USD",
      rail: "stripe",
      description: "Purchase of certified synthetic dataset",
      metadata: { "cdp:source_system": "partner_portal" },
    },
    { idempotencyKey: "intent-synthetic-dataset-001" }
  );

  console.log("Created payment intent:", intent.id);
  console.log("Status:", intent.status);

  // 2. Confirm it
  const confirmed = await client.paymentIntents.confirm(intent.id, {
    idempotencyKey: `confirm-${intent.id}`,
  });

  console.log("Confirmed payment intent:", confirmed.id);
  console.log("Status:", confirmed.status);
}

main().catch(console.error);
