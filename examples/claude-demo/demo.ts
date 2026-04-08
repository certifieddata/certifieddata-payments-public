#!/usr/bin/env tsx
/**
 * CertifiedData Agent Commerce — End-to-End Demo (TypeScript)
 *
 * Demonstrates the 5-phase agent payment workflow using the live SDK.
 *
 * Setup:
 *   pnpm install
 *
 * Run:
 *   CDAC_API_KEY=cdp_test_xxx tsx examples/claude-demo/demo.ts
 *   # against sandbox:
 *   CDAC_API_KEY=cdp_test_xxx CDAC_BASE_URL=https://sandbox.certifieddata.io \
 *     tsx examples/claude-demo/demo.ts
 *
 * Phases:
 *   1 — Agent declares intent (create transaction)
 *   2 — Attach provenance links (bind decision record)
 *   3 — Policy evaluation + authorization
 *   4 — Execute — settlement + inline signed receipt
 *   5 — Independent verification (public, no auth)
 */

import { CertifiedDataAgentCommerceClient } from "@certifieddata/payments";

const BASE_URL = process.env["CDAC_BASE_URL"] ?? "https://certifieddata.io";

const C = {
  reset:  "\x1b[0m",
  bold:   "\x1b[1m",
  green:  "\x1b[32m",
  cyan:   "\x1b[36m",
  grey:   "\x1b[90m",
  red:    "\x1b[31m",
};

function log(phase: string, msg: string): void {
  console.log(`\n${C.bold}${C.cyan}${phase}${C.reset}  ${msg}`);
}

function ok(label: string, detail: string): void {
  console.log(`  ${C.green}✓${C.reset}  ${C.bold}${label}${C.reset}  ${detail}`);
}

function fail(label: string, detail: string): never {
  console.error(`\n  ${C.red}✗${C.reset}  ${C.bold}${label}${C.reset}  ${detail}`);
  process.exit(1);
}

async function main(): Promise<void> {
  console.log(`\n${C.bold}CertifiedData Agent Commerce — Demo${C.reset}`);
  console.log(`${C.grey}Target: ${BASE_URL}${C.reset}`);
  console.log(`${C.grey}SDK:    @certifieddata/payments${C.reset}`);

  // Init client — reads CDAC_API_KEY + CDAC_BASE_URL from env
  let client: CertifiedDataAgentCommerceClient;
  try {
    client = new CertifiedDataAgentCommerceClient();
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    console.error(`\n  ${C.red}Config error:${C.reset} ${msg}`);
    console.error("  Set:  export CDAC_API_KEY=cdp_test_xxx");
    process.exit(1);
  }

  // ── Phase 1: Agent declares intent ─────────────────────────────────────────
  log("Phase 1", "Agent declares intent — what, why, how much");

  const tx = await client.transactions.create({
    amount:   2500,    // cents ($25.00)
    currency: "usd",
    rail:     "stripe",
  }, { idempotencyKey: `demo-${Date.now()}` });

  const txId = tx.id;
  ok("transaction_created", `id=${txId}  status=${tx.status}`);

  // ── Phase 2: Attach provenance links ────────────────────────────────────────
  log("Phase 2", "Attach provenance — bind decision record to payment");

  await client.transactions.attachLinks(txId, {
    decision_id: "dec_agent_demo_2026",
    artifact_id: "art_gpu_compute_001",
  });
  ok("links_attached", "decision_id=dec_agent_demo_2026  artifact_id=art_gpu_compute_001");
  console.log(`  ${C.grey}  This links the AI system's decision lineage to the financial action.${C.reset}`);

  // ── Phase 3 + 4: Capture ────────────────────────────────────────────────────
  log("Phase 3 + 4", "capture() — policy eval → authorize → execute → inline signed receipt");
  console.log(`  ${C.grey}→ POST /v1/transactions/${txId}/capture${C.reset}`);

  const capture = await client.transactions.capture(txId).catch((e: unknown) => {
    const msg = e instanceof Error ? e.message : String(e);
    fail("capture", `API error: ${msg}`);
  });

  const status  = (capture as Record<string, unknown>).status as string;
  const receipt = (capture as Record<string, unknown>).receipt as Record<string, unknown> | undefined;

  if (!receipt)             fail("receipt",    "receipt not inlined in capture response");
  const receiptId = (receipt["receipt_id"] ?? receipt["id"]) as string | undefined;
  if (!receiptId)           fail("receipt_id", "receipt_id missing from receipt payload");

  ok("settled",        `transaction_id=${txId}  status=${status}`);
  ok("receipt_inline", `receipt_id=${receiptId}`);

  console.log(`\n${C.grey}Signed receipt (inline, no second fetch):${C.reset}`);
  console.log(C.grey + JSON.stringify(receipt, null, 2) + C.reset);

  // ── Phase 5: Independent verification — raw fetch, no SDK ──────────────────
  log("Phase 5", "Independent verification — Ed25519 + SHA-256, no auth required");
  const verifyUrl = `${BASE_URL}/api/payments/verify/${receiptId}`;
  console.log(`  ${C.grey}→ GET ${verifyUrl}  (public endpoint, no auth)${C.reset}`);

  const verifyRes = await fetch(verifyUrl);
  if (!verifyRes.ok) {
    const text = await verifyRes.text().catch(() => "");
    fail("verify_request", `HTTP ${verifyRes.status}: ${text}`);
  }
  const verify = await verifyRes.json() as Record<string, unknown>;

  if (!verify["hashValid"])      fail("hash_integrity", "hashValid=false — receipt payload may have been tampered");
  if (!verify["signatureValid"]) fail("ed25519_sig",    "signatureValid=false — Ed25519 signature invalid");
  if (!verify["valid"])          fail("verify_overall", "valid=false — overall verification failed");

  ok("hash_integrity", "hashValid=true    SHA-256 matches stored payload");
  ok("ed25519_sig",    "signatureValid=true  Ed25519 verified against public key");
  ok("verify_overall", "valid=true  receipt is tamper-evident and independently verifiable");

  // ── Summary ─────────────────────────────────────────────────────────────────
  console.log(`\n${"─".repeat(60)}`);
  console.log(`${C.bold}${C.green}All 5 phases passed${C.reset}`);
  console.log(`\n  Receipt ID:   ${receiptId}`);
  console.log(`  Verify URL:   ${verifyUrl}`);
  console.log(`  Signed by:    ${verify["signingKeyId"] ?? "cd_root_2026"}  (Ed25519)`);
  console.log(`\n  ${C.grey}The agent transacted. The receipt proves it — cryptographically.${C.reset}\n`);
}

main().catch((err: unknown) => {
  const msg = err instanceof Error ? err.message : String(err);
  console.error(`${C.red}Demo fatal:${C.reset}`, msg);
  process.exit(1);
});
