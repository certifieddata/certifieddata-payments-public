// Aligns with apps/api/src/services/payments/types.ts in the private platform

export type PaymentRail = "stripe" | "usdc_base" | "usdc_ethereum" | "eth_ethereum";

export type TransactionStatus = "created" | "submitted" | "captured" | "succeeded" | "failed" | "canceled";

export type PaymentIntentStatus = "created" | "confirmed" | "processing" | "succeeded" | "failed" | "canceled";

export type SettlementStatus = "draft" | "submitted" | "processing" | "succeeded" | "failed" | "canceled";

export type RefundStatus = "created" | "processing" | "succeeded" | "failed";

export type PayeeStatus = "pending" | "active" | "suspended" | "inactive";

export type KycStatus = "not_started" | "pending" | "approved" | "rejected";

export type PayoutDestinationStatus = "pending_verification" | "active" | "rejected" | "inactive";

export type InvoiceStatus = "draft" | "open" | "paid" | "void" | "uncollectible";

export type Environment = "sandbox" | "live";

export type ActorType = "api_key" | "external_client" | "internal_service";

/** Schema version for the payment receipt artifact. Aligns with private platform's payment_receipt.v1 */
export const RECEIPT_SCHEMA_VERSION = "payment_receipt.v1" as const;
export type ReceiptSchemaVersion = typeof RECEIPT_SCHEMA_VERSION;

/** Namespaced provenance metadata. Keys must use cdp:, partner:, or ext: prefix. */
export type ProvenanceMetadata = {
  [key: `cdp:${string}` | `partner:${string}` | `ext:${string}`]: string;
};

export interface ProvenanceLinkSet {
  artifact_id?: string | null;
  certificate_id?: string | null;
  decision_record_id?: string | null;
  decision_id?: string | null;
  dataset_id?: string | null;
  model_id?: string | null;
  output_id?: string | null;
  /** SHA-256 digest of canonical receipt payload. Format: sha256:{hex} */
  receipt_hash?: string | null;
  /** Freeform external reference. Max 128 chars. */
  external_reference?: string | null;
  provenance_metadata?: ProvenanceMetadata | null;
}

export interface RequestContext {
  request_id: string;
  idempotency_key?: string | null;
  api_key_prefix: string;
  origin: string;
  actor_type: ActorType;
}

export interface PaginationEnvelope<T> {
  data: T[];
  has_more: boolean;
  next_cursor: string | null;
  total_count?: number | null;
}

export interface ListParams {
  limit?: number;
  starting_after?: string;
}

/** Monetary amount with ISO 4217 currency code. */
export interface Money {
  /** Amount in the smallest currency unit (e.g. cents for USD). */
  amount: number;
  /** ISO 4217 currency code (e.g. "USD", "EUR"). */
  currency: string;
}
