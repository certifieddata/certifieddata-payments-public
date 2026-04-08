/**
 * Example: Agentic payee onboarding — create a payee and register an alias.
 *
 * This pattern enables agent-to-agent workflows where external systems
 * look up payees by their own reference IDs rather than CDP IDs.
 *
 * Run against mock server:
 *   npx tsx examples/agentic-payee-onboarding/create-payee-with-alias.ts
 */

import { CertifiedDataAgentCommerceClient } from "@certifieddata/payments";

const client = new CertifiedDataAgentCommerceClient({
  apiKey: "cdp_test_example_key",
  baseUrl: "http://localhost:3456",
});

async function onboardPayeeWithAlias(params: {
  legal_name: string;
  email: string;
  external_system: string;
  external_ref: string;
}) {
  const idempotencyBase = `onboard-${params.external_system}-${params.external_ref}`;

  // 1. Create the payee
  const payee = await client.payees.create(
    {
      entity_type: "company",
      legal_name: params.legal_name,
      email: params.email,
      default_payout_method: "stripe",
      metadata: {
        "cdp:source_system": params.external_system,
        [`partner:${params.external_system}_ref`]: params.external_ref,
      },
    },
    { idempotencyKey: `${idempotencyBase}-create` }
  );

  // 2. Register an alias so downstream systems can look up the payee
  const alias = await client.payees.createAlias(
    payee.id,
    {
      external_system: params.external_system,
      external_ref: params.external_ref,
    },
    { idempotencyKey: `${idempotencyBase}-alias` }
  );

  return { payee, alias };
}

async function main() {
  const { payee, alias } = await onboardPayeeWithAlias({
    legal_name: "NovaMind Research, Inc.",
    email: "billing@novamind.example",
    external_system: "partner_portal",
    external_ref: "vendor_NVR_9821",
  });

  console.log("Payee created:", payee.id);
  console.log("Alias created:", alias.id);
  console.log(`  ${alias.external_system} → ${alias.external_ref} → ${alias.payee_id}`);
}

main().catch(console.error);
