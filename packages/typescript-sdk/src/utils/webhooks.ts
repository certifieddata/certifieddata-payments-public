/**
 * Webhook signature verification for CertifiedData Payments.
 *
 * Signing algorithm: HMAC-SHA256
 * Signed payload: {timestamp}.{raw_body}
 * Signature header: CDP-Signature: t={timestamp},v1={hmac_sha256}
 * Timestamp header: CDP-Timestamp: {unix_timestamp}
 * Tolerance: 300 seconds
 *
 * See test-vectors/webhook-signature/ for verified test cases.
 */

export interface VerifyWebhookSignatureParams {
  /** The raw request body string (not parsed). */
  payload: string;
  /** The CDP-Signature header value: t={timestamp},v1={hmac} */
  signature: string;
  /** The CDP-Timestamp header value (unix timestamp string). */
  timestamp: string;
  /** The webhook endpoint secret. */
  secret: string;
  /** Timestamp tolerance in seconds. Defaults to 300. */
  toleranceSeconds?: number;
}

export interface VerifyWebhookSignatureResult {
  valid: boolean;
  reason?: string;
}

/**
 * Verify a CDP webhook signature.
 *
 * @example
 * const result = verifyWebhookSignature({
 *   payload: rawBody,
 *   signature: req.headers["cdp-signature"],
 *   timestamp: req.headers["cdp-timestamp"],
 *   secret: process.env.CDP_WEBHOOK_SECRET,
 * });
 * if (!result.valid) throw new Error("Invalid signature");
 */
export async function verifyWebhookSignature(
  params: VerifyWebhookSignatureParams
): Promise<VerifyWebhookSignatureResult> {
  const { payload, signature, timestamp, secret, toleranceSeconds = 300 } = params;

  // Check timestamp tolerance
  const ts = parseInt(timestamp, 10);
  if (isNaN(ts)) {
    return { valid: false, reason: "Invalid timestamp" };
  }

  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - ts) > toleranceSeconds) {
    return { valid: false, reason: "Timestamp outside tolerance window" };
  }

  // Parse signature header: t={timestamp},v1={hmac}
  const v1Match = signature.match(/v1=([a-f0-9]+)/);
  if (!v1Match?.[1]) {
    return { valid: false, reason: "No v1 signature found in header" };
  }

  const expectedHex = v1Match[1];

  // Compute expected signature
  const signedPayload = `${timestamp}.${payload}`;
  const encoder = new TextEncoder();
  const keyData = encoder.encode(secret);
  const messageData = encoder.encode(signedPayload);

  // Use globalThis.crypto (Web Crypto API, available in Node.js ≥ 18)
  const subtle = globalThis.crypto.subtle;

  const cryptoKey = await subtle.importKey(
    "raw",
    keyData,
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const signatureBuffer = await subtle.sign("HMAC", cryptoKey, messageData);
  const computedHex = Array.from(new Uint8Array(signatureBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");

  // Constant-time comparison
  if (computedHex.length !== expectedHex.length) {
    return { valid: false, reason: "Signature mismatch" };
  }

  let mismatch = 0;
  for (let i = 0; i < computedHex.length; i++) {
    mismatch |= computedHex.charCodeAt(i) ^ expectedHex.charCodeAt(i);
  }

  if (mismatch !== 0) {
    return { valid: false, reason: "Signature mismatch" };
  }

  return { valid: true };
}
