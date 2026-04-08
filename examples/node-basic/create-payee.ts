/**
 * Example: Create a payee using the CertifiedData Agent Commerce TypeScript SDK.
 *
 * Run against mock server:
 *   pnpm --filter @certifieddata/agent-commerce-mock-server start
 *   npx tsx examples/node-basic/create-payee.ts
 */

import { CertifiedDataAgentCommerceClient } from "@certifieddata/payments";

const client = new CertifiedDataAgentCommerceClient({
  apiKey: "cdp_test_example_key",
  baseUrl: "http://localhost:3456",
});

async function main() {
  const payee = await client.payees.create(
    {
      entity_type: "company",
      legal_name: "Atlas Synthetic Labs, Inc.",
      email: "payments@atlas-synthetic.example",
      default_payout_method: "stripe",
      metadata: {
        "cdp:source_system": "partner_portal",
        "partner:account_ref": "atlas-001",
      },
    },
    { idempotencyKey: "create-payee-atlas-001" }
  );

  console.log("Created payee:", payee.id);
  console.log("Status:", payee.status);
  console.log("KYC status:", payee.kyc_status);
}

main().catch(console.error);
