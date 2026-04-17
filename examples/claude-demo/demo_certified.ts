#!/usr/bin/env tsx
/**
 * CertifiedData Agent Commerce — Certified Artifact Purchase Demo (TypeScript)
 *
 * Binds certificate_id + artifact_id + decision_record_id to a transaction
 * before capture, then verifies the resulting signed receipt.
 *
 * Run:
 *   tsx examples/claude-demo/demo_certified.ts
 *   CDAC_BASE_URL=http://localhost:3456 tsx examples/claude-demo/demo_certified.ts
 */

import { CertifiedDataAgentCommerceClient } from "../../packages/typescript-sdk/src/index.js";

const DEMO_KEY = "cdp_test_demo_certifieddata_io_2026";
if (!process.env["CDAC_API_KEY"]) process.env["CDAC_API_KEY"] = DEMO_KEY;

const BASE_URL = (process.env["CDAC_BASE_URL"] ?? "https://certifieddata.io").replace(/\/+$/, "");

const C = {
  reset: "\x1b[0m", bold: "\x1b[1m",
  green: "\x1b[32m", cyan: "\x1b[36m", grey: "\x1b[90m",
  red: "\x1b[31m", yel: "\x1b[33m",
};

const log  = (phase: string, msg: string) => console.log(`\n${C.bold}${C.cyan}${phase}${C.reset}  ${msg}`);
const ok   = (l: string, d: string)       => console.log(`  ${C.green}✓${C.reset}  ${C.bold}${l}${C.reset}  ${d}`);
const warn = (l: string, d: string)       => console.log(`  ${C.yel}!${C.reset}  ${C.bold}${l}${C.reset}  ${d}`);
const fail = (l: string, d: string): never => { console.error(`\n  ${C.red}✗${C.reset}  ${C.bold}${l}${C.reset}  ${d}`); process.exit(1); };

function modeLabel(url: string): string {
  const u = url.toLowerCase();
  if (u.includes("localhost") || u.includes("127.0.0.1")) return "local mock";
  if (u.includes("sandbox")) return "sandbox";
  return "live";
}

async function main(): Promise<void> {
  console.log(`\n${C.bold}CertifiedData Agent Commerce — Certified Artifact Purchase${C.reset}`);
  console.log(`${C.grey}Profile: certified-artifact-purchase (v1.0.0)${C.reset}`);
  console.log(`${C.grey}Mode:    ${modeLabel(BASE_URL)}${C.reset}`);
  console.log(`${C.grey}Target:  ${BASE_URL}${C.reset}`);

  const client = new CertifiedDataAgentCommerceClient();

  const certificateId    = "cert_01HXZ803C0R6V4K4P9HWB6J5N6";
  const artifactId       = "art_01HXZ7Z8R2QQSN5B3T5VQ4D1WA";
  const decisionRecordId = `dec_demo_${Math.floor(Date.now() / 1000)}`;

  log("Phase 1", "Declare intent — purchase of a certified synthetic dataset");
  const tx = await client.transactions.create(
    { amount: 4900, currency: "usd", rail: "stripe",
      description: "Certified synthetic dataset v2 — CDAC profile" },
    { idempotencyKey: `demo-cert-${Date.now()}` }
  );
  ok("transaction_created", `id=${tx.id}  status=${tx.status}`);

  log("Phase 2", "Attach full provenance — certificate + artifact + decision");
  await client.transactions.attachLinks(tx.id, {
    certificate_id: certificateId,
    artifact_id:    artifactId,
    decision_record_id: decisionRecordId,
    provenance_metadata: {
      "cdp:workflow_id":     "wf_certified_demo",
      "cdp:source_system":   "certifieddata-agent-commerce-public",
      "partner:invoice_ref": "INV-DEMO-001",
    },
  });
  ok("certificate_id",     certificateId);
  ok("artifact_id",        artifactId);
  ok("decision_record_id", decisionRecordId);

  log("Phase 3 + 4", "capture() — policy eval → authorize → execute → inline receipt");
  const cap = await client.transactions.capture(tx.id);
  const receipt = (cap as Record<string, unknown>)["receipt"] as Record<string, unknown> | undefined;
  if (!receipt) fail("receipt", "inline receipt missing");
  const receiptId = receipt["receipt_id"] as string | undefined;
  if (!receiptId) fail("receipt_id", "missing receipt_id");

  for (const field of ["certificate_id", "artifact_id"]) {
    if (!receipt[field]) warn(`receipt.${field}`, "not surfaced in receipt — check transaction.provenance");
  }
  ok("receipt_inline", `receipt_id=${receiptId}`);
  ok("lineage_bound",  `decision_record_id=${String(receipt["decision_record_id"])}`);
  console.log(`\n${C.grey}Receipt JSON:${C.reset}`);
  console.log(C.grey + JSON.stringify(receipt, null, 2) + C.reset);

  log("Phase 5", "Public verification");
  const verifyUrl = `${BASE_URL}/api/payments/verify/${receiptId}`;
  const res = await fetch(verifyUrl);
  if (!res.ok) fail("verify", `HTTP ${res.status}`);
  const v = await res.json() as Record<string, unknown>;
  if (!v["valid"]) fail("verify", `valid=false hashValid=${v["hashValid"]} sigValid=${v["signatureValid"]}`);
  ok("verify_overall", "valid=true (Ed25519 + SHA-256)");
  ok("signing_key",    `signingKeyId=${String(v["signingKeyId"] ?? "?")}`);

  console.log(`\n${"─".repeat(60)}`);
  console.log(`${C.bold}${C.green}Certified artifact purchase — all phases passed${C.reset}`);
  console.log(`  Transaction:     ${tx.id}`);
  console.log(`  Receipt:         ${receiptId}`);
  console.log(`  Certificate:     ${certificateId}`);
  console.log(`  Artifact:        ${artifactId}`);
  console.log(`  Decision Record: ${decisionRecordId}`);
  console.log(`  Verify URL:      ${verifyUrl}\n`);
}

main().catch((e: unknown) => {
  const msg = e instanceof Error ? e.message : String(e);
  console.error(`${C.red}Demo fatal:${C.reset}`, msg);
  process.exit(1);
});
