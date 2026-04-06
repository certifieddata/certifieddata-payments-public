/**
 * Example: Verify an incoming CDP webhook signature.
 *
 * Uses the test vector from:
 *   test-vectors/webhook-signature/valid-vector-001.json
 *
 * In production, use the secret from your webhook endpoint (only returned at creation time).
 *
 * Run:
 *   npx tsx examples/node-webhooks/verify-webhook.ts
 */

import { verifyWebhookSignature } from "@certifieddata/payments";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));

async function main() {
  // Load the test vector
  const vectorPath = join(__dirname, "../../test-vectors/webhook-signature/valid-vector-001.json");
  const vector = JSON.parse(await readFile(vectorPath, "utf-8"));

  const rawBody = vector.payload;
  const timestamp = vector.timestamp;
  const expectedSigHeader = vector.expected_signature_header;
  const secret = "whsec_test_example_secret_32bytes_xx"; // matches the vector secret

  const isValid = await verifyWebhookSignature(
    rawBody,
    expectedSigHeader,
    timestamp,
    secret,
    // Disable timestamp tolerance for test vector validation
    Number.MAX_SAFE_INTEGER
  );

  if (isValid) {
    console.log("Webhook signature is VALID");
  } else {
    console.error("Webhook signature is INVALID");
    process.exit(1);
  }

  // Example of how you'd use this in an Express handler:
  console.log("\nExample Express handler:");
  console.log(`
app.post("/webhooks/cdp", express.raw({ type: "application/json" }), async (req, res) => {
  const rawBody = req.body.toString("utf-8");
  const signature = req.headers["cdp-signature"] as string;
  const timestamp = req.headers["cdp-timestamp"] as string;

  const isValid = await verifyWebhookSignature(rawBody, signature, timestamp, process.env.CDP_WEBHOOK_SECRET!);

  if (!isValid) {
    return res.status(400).json({ error: "Invalid webhook signature" });
  }

  const event = JSON.parse(rawBody);
  console.log("Received event:", event.event_type, event.id);

  res.status(200).json({ received: true });
});
  `);
}

main().catch(console.error);
