import type {
  PaymentRail,
  TransactionStatus,
  PaymentIntentStatus,
  SettlementStatus,
  RefundStatus,
  PayeeStatus,
  KycStatus,
  PayoutDestinationStatus,
  InvoiceStatus,
  ProvenanceLinkSet,
  RequestContext,
  ReceiptSchemaVersion,
} from "./common.js";

// ─── Payee ───────────────────────────────────────────────────────────────────

export interface Payee {
  id: string;
  object: "payee";
  entity_type: "individual" | "company";
  legal_name?: string | null;
  email?: string | null;
  status: PayeeStatus;
  kyc_status: KycStatus;
  default_payout_method?: PaymentRail | null;
  metadata?: Record<string, string> | null;
  created_at: string;
  updated_at: string;
  livemode: boolean;
}

export interface CreatePayeeParams {
  entity_type: "individual" | "company";
  legal_name?: string;
  email?: string;
  default_payout_method?: PaymentRail;
  metadata?: Record<string, string>;
}

// ─── PayeeAlias ───────────────────────────────────────────────────────────────

export interface PayeeAlias {
  id: string;
  object: "payee_alias";
  payee_id: string;
  external_system: string;
  external_ref: string;
  created_at: string;
}

export interface CreatePayeeAliasParams {
  external_system: string;
  external_ref: string;
}

// ─── PayoutDestination ────────────────────────────────────────────────────────

export interface PayoutDestination {
  id: string;
  object: "payout_destination";
  payee_id: string;
  rail_type: PaymentRail;
  status: PayoutDestinationStatus;
  is_default: boolean;
  version: number;
  processor_ref?: string | null;
  metadata?: Record<string, string> | null;
  created_at: string;
  updated_at: string;
}

export interface CreatePayoutDestinationParams {
  rail_type: PaymentRail;
  is_default?: boolean;
  processor_ref?: string;
  metadata?: Record<string, string>;
}

// ─── Customer ─────────────────────────────────────────────────────────────────

export interface Customer {
  id: string;
  object: "customer";
  email?: string | null;
  name?: string | null;
  status: "active" | "inactive";
  metadata?: Record<string, string> | null;
  created_at: string;
  updated_at: string;
  livemode: boolean;
}

export interface CreateCustomerParams {
  email?: string;
  name?: string;
  metadata?: Record<string, string>;
}

// ─── Invoice ──────────────────────────────────────────────────────────────────

export interface Invoice {
  id: string;
  object: "invoice";
  payee_id: string;
  customer_id?: string | null;
  amount: number;
  currency: string;
  status: InvoiceStatus;
  description?: string | null;
  payment_intent_id?: string | null;
  metadata?: Record<string, string> | null;
  finalized_at?: string | null;
  voided_at?: string | null;
  created_at: string;
  updated_at: string;
  livemode: boolean;
}

export interface CreateInvoiceParams {
  payee_id: string;
  customer_id?: string;
  amount: number;
  currency: string;
  description?: string;
  metadata?: Record<string, string>;
}

// ─── PaymentIntent ────────────────────────────────────────────────────────────

export interface PaymentIntent {
  id: string;
  object: "payment_intent";
  customer_id?: string | null;
  payee_id?: string | null;
  invoice_id?: string | null;
  amount: number;
  currency: string;
  rail: PaymentRail;
  status: PaymentIntentStatus;
  description?: string | null;
  transaction_id?: string | null;
  metadata?: Record<string, string> | null;
  created_at: string;
  updated_at: string;
  livemode: boolean;
}

export interface CreatePaymentIntentParams {
  customer_id?: string;
  payee_id?: string;
  amount: number;
  currency: string;
  rail: PaymentRail;
  description?: string;
  metadata?: Record<string, string>;
}

// ─── Receipt (embedded sub-object) ───────────────────────────────────────────

export interface ReceiptSubObject {
  id: string;
  schema_version: ReceiptSchemaVersion;
  hash: string;
  created_at: string;
}

// ─── Transaction ──────────────────────────────────────────────────────────────

export interface Transaction {
  id: string;
  object: "transaction";
  payment_intent_id?: string | null;
  payee_id?: string | null;
  customer_id?: string | null;
  amount: number;
  currency: string;
  rail: PaymentRail;
  status: TransactionStatus;
  description?: string | null;
  provenance?: ProvenanceLinkSet | null;
  receipt?: ReceiptSubObject | null;
  metadata?: Record<string, string> | null;
  created_at: string;
  updated_at: string;
  livemode: boolean;
}

export interface CreateTransactionParams {
  payment_intent_id?: string;
  payee_id?: string;
  /**
   * The agent initiating this transaction.
   * Optional — the platform auto-resolves to your account's first active agent
   * if omitted. Supply explicitly when managing multiple agents.
   */
  agent_id?: string;
  amount: number;
  currency: string;
  rail: PaymentRail;
  purpose?: string;
  purpose_tag?: string;
  description?: string;
  idempotency_key?: string;
  metadata?: Record<string, string>;
}

// ─── Settlement ───────────────────────────────────────────────────────────────

export interface Settlement {
  id: string;
  object: "settlement";
  payee_id: string;
  destination_id?: string | null;
  amount: number;
  currency: string;
  status: SettlementStatus;
  transaction_ids: string[];
  provenance?: ProvenanceLinkSet | null;
  metadata?: Record<string, string> | null;
  submitted_at?: string | null;
  succeeded_at?: string | null;
  created_at: string;
  updated_at: string;
  livemode: boolean;
}

export interface CreateSettlementParams {
  payee_id: string;
  destination_id?: string;
  amount: number;
  currency: string;
  transaction_ids: string[];
  metadata?: Record<string, string>;
}

// ─── Refund ───────────────────────────────────────────────────────────────────

export interface Refund {
  id: string;
  object: "refund";
  transaction_id: string;
  amount: number;
  currency: string;
  status: RefundStatus;
  reason?: "duplicate" | "fraudulent" | "customer_request" | "partial_adjustment" | null;
  metadata?: Record<string, string> | null;
  succeeded_at?: string | null;
  created_at: string;
  updated_at: string;
  livemode: boolean;
}

export interface CreateRefundParams {
  transaction_id: string;
  amount: number;
  reason?: "duplicate" | "fraudulent" | "customer_request" | "partial_adjustment";
  metadata?: Record<string, string>;
}

// ─── Event ────────────────────────────────────────────────────────────────────

export interface Event {
  id: string;
  object: "event";
  event_type: string;
  event_version: string;
  api_version: string;
  occurred_at: string;
  environment: "sandbox" | "live";
  livemode: boolean;
  resource_type: string;
  resource_id: string;
  data: Record<string, unknown>;
  provenance?: ProvenanceLinkSet | null;
  request_context?: RequestContext | null;
}

// ─── WebhookEndpoint ──────────────────────────────────────────────────────────

export interface WebhookEndpoint {
  id: string;
  object: "webhook_endpoint";
  url: string;
  enabled_events: string[];
  status: "enabled" | "disabled";
  description?: string | null;
  /** Only present at creation time. Null on all subsequent reads. */
  secret?: string | null;
  created_at: string;
  updated_at: string;
  livemode: boolean;
}

export interface CreateWebhookEndpointParams {
  url: string;
  enabled_events: string[];
  description?: string;
}
