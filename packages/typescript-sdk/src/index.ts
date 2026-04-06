// ─── Client ───────────────────────────────────────────────────────────────────
export { CertifiedDataPaymentsClient } from "./client.js";
export type { CertifiedDataPaymentsClientOptions } from "./client.js";

// ─── Types — Common ───────────────────────────────────────────────────────────
export type {
  PaymentRail,
  TransactionStatus,
  PaymentIntentStatus,
  SettlementStatus,
  RefundStatus,
  PayeeStatus,
  KycStatus,
  PayoutDestinationStatus,
  InvoiceStatus,
  Money,
  PaginationEnvelope,
  ListParams,
  ProvenanceMetadata,
  ProvenanceLinkSet,
  RequestContext,
  ReceiptSchemaVersion,
} from "./types/common.js";

export { RECEIPT_SCHEMA_VERSION } from "./types/common.js";

// ─── Types — Resources ────────────────────────────────────────────────────────
export type {
  Payee,
  CreatePayeeParams,
  PayeeAlias,
  CreatePayeeAliasParams,
  PayoutDestination,
  CreatePayoutDestinationParams,
  Customer,
  CreateCustomerParams,
  Invoice,
  CreateInvoiceParams,
  PaymentIntent,
  CreatePaymentIntentParams,
  ReceiptSubObject,
  Transaction,
  CreateTransactionParams,
  Settlement,
  CreateSettlementParams,
  Refund,
  CreateRefundParams,
  Event,
  WebhookEndpoint,
  CreateWebhookEndpointParams,
} from "./types/resources.js";

// ─── Capabilities ─────────────────────────────────────────────────────────────
export type {
  HealthResponse,
  CapabilitiesResponse,
  VersionResponse,
} from "./resources/capabilities.js";

// ─── Errors ───────────────────────────────────────────────────────────────────
export {
  CDPError,
  CDPAuthError,
  CDPValidationError,
  CDPNotFoundError,
  CDPConflictError,
  CDPRateLimitError,
  createCDPError,
} from "./errors/base.js";

// ─── Utilities ────────────────────────────────────────────────────────────────
export { verifyWebhookSignature } from "./utils/webhooks.js";
export { listAll } from "./utils/pagination.js";
