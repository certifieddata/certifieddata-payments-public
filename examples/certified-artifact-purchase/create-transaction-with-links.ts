/**
 * End-to-end example: Certified artifact purchase with provenance linking.
 *
 * Flow:
 *   1. Create a payee
 *   2. Create a payment intent
 *   3. Create a transaction
 *   4. Attach provenance links (certificate_id, artifact_id)
 *   5. Capture the transaction → receipt issued
 *
 * Run against mock server:
 *   npx tsx examples/certified-artifact-purchase/create-transaction-with-links.ts
 */

import { CertifiedDataAgentCommerceClient } from "@certifieddata/payments";

const client = new CertifiedDataAgentCommerceClient({
  apiKey: "cdp_test_example_key",
  baseUrl: "http://localhost:3456",
});

async function main() {
  // 1. Create a payee (artifact vendor)
  const payee = await client.payees.create(
    {
      entity_type: "company",
      legal_name: "Atlas Synthetic Labs, Inc.",
      email: "payments@atlas-synthetic.example",
      default_payout_method: "stripe",
    },
    { idempotencyKey: "payee-atlas-certified-purchase-001" }
  );
  console.log("Payee:", payee.id);

  // 2. Create a payment intent
  const intent = await client.paymentIntents.create(
    {
      amount: 4900, // $49.00
      currency: "USD",
      rail: "stripe",
      payee_id: payee.id,
      description: "Purchase of certified synthetic dataset v2",
    },
    { idempotencyKey: "intent-certified-purchase-001" }
  );
  console.log("Payment intent:", intent.id);

  // 3. Create a transaction
  const transaction = await client.transactions.create(
    {
      payment_intent_id: intent.id,
      payee_id: payee.id,
      amount: 4900,
      currency: "USD",
      rail: "stripe",
      description: "Certified synthetic dataset v2 purchase",
    },
    { idempotencyKey: "tx-certified-purchase-001" }
  );
  console.log("Transaction:", transaction.id, "Status:", transaction.status);

  // 4. Attach provenance links — must happen BEFORE capture
  const withLinks = await client.transactions.attachLinks(
    transaction.id,
    {
      certificate_id: "cert_01HXZ803C0R6V4K4P9HWB6J5N6",
      artifact_id: "art_01HXZ7Z8R2QQSN5B3T5VQ4D1WA",
      decision_id: "dec_01HXZ80MCP6KNB8M3D0W1MSZV9",
      provenance_metadata: {
        "cdp:workflow_id": "wf_certified_purchase_001",
        "cdp:source_system": "certifieddata-platform",
        "partner:invoice_ref": "INV-2026-001",
      },
    },
    { idempotencyKey: `attach-links-${transaction.id}` }
  );
  console.log("Provenance attached:", JSON.stringify(withLinks.provenance, null, 2));

  // 5. Capture the transaction → receipt is issued
  const captured = await client.transactions.capture(transaction.id, {
    idempotencyKey: `capture-${transaction.id}`,
  });
  console.log("Captured:", captured.id, "Status:", captured.status);
  console.log("Receipt:", JSON.stringify(captured.receipt, null, 2));
}

main().catch(console.error);
