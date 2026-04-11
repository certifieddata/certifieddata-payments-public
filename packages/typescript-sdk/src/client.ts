import type { CDPClientConfig } from "./utils/request.js";
import { PayeesResource } from "./resources/payees.js";
import { PaymentIntentsResource } from "./resources/payment-intents.js";
import { TransactionsResource } from "./resources/transactions.js";
import { SettlementsResource } from "./resources/settlements.js";
import { RefundsResource } from "./resources/refunds.js";
import { EventsResource } from "./resources/events.js";
import { WebhooksResource } from "./resources/webhooks.js";
import { CapabilitiesResource } from "./resources/capabilities.js";
import { verifyWebhookSignature, type VerifyWebhookSignatureResult } from "./utils/webhooks.js";

export interface CertifiedDataAgentCommerceClientOptions {
  /**
   * CDP API key — use `cdp_test_...` for sandbox, `cdp_live_...` for production.
   * Reads `CDAC_API_KEY` from the environment if omitted.
   */
  apiKey?: string;
  /**
   * API base URL. Reads `CDAC_BASE_URL` from the environment if omitted.
   * Defaults to `https://certifieddata.io`.
   * Both test (`cdp_test_`) and live (`cdp_live_`) keys route through the same host.
   */
  baseUrl?: string;
  /** API version header value. Defaults to `2025-01-01`. */
  apiVersion?: string;
  /** Idempotency key to attach to every mutating request on this client instance */
  idempotencyKey?: string;
}

export class CertifiedDataAgentCommerceClient {
  readonly payees: PayeesResource;
  readonly paymentIntents: PaymentIntentsResource;
  readonly transactions: TransactionsResource;
  readonly settlements: SettlementsResource;
  readonly refunds: RefundsResource;
  readonly events: EventsResource;
  readonly webhooks: WebhooksResource;
  readonly capabilities: CapabilitiesResource;

  private readonly config: CDPClientConfig;

  constructor(options: CertifiedDataAgentCommerceClientOptions = {}) {
    const key = options.apiKey ?? process.env["CDAC_API_KEY"];
    if (!key) {
      throw new Error("apiKey is required. Pass it directly or set CDAC_API_KEY.");
    }
    this.config = {
      apiKey: key,
      baseUrl: options.baseUrl ?? process.env["CDAC_BASE_URL"] ?? "https://certifieddata.io",
      apiVersion: options.apiVersion ?? "2025-01-01",
      ...(options.idempotencyKey !== undefined ? { idempotencyKey: options.idempotencyKey } : {}),
    };

    this.payees = new PayeesResource(this.config);
    this.paymentIntents = new PaymentIntentsResource(this.config);
    this.transactions = new TransactionsResource(this.config);
    this.settlements = new SettlementsResource(this.config);
    this.refunds = new RefundsResource(this.config);
    this.events = new EventsResource(this.config);
    this.webhooks = new WebhooksResource(this.config);
    this.capabilities = new CapabilitiesResource(this.config);
  }

  /**
   * Returns a new client instance with the given idempotency key attached.
   * All mutating requests made through the returned client will automatically
   * include this key.
   *
   * @example
   * const idempotent = client.withIdempotencyKey("order-001-pay");
   * await idempotent.transactions.create({ ... });
   */
  withIdempotencyKey(key: string): CertifiedDataAgentCommerceClient {
    return new CertifiedDataAgentCommerceClient({
      apiKey:         this.config.apiKey,
      baseUrl:        this.config.baseUrl,
      apiVersion:     this.config.apiVersion,
      idempotencyKey: key,
    });
  }

  /**
   * Verify an incoming CDP webhook signature.
   *
   * @param rawBody - Raw request body string (before JSON.parse)
   * @param signatureHeader - `CDAC-Signature` header value
   * @param timestampHeader - `CDAC-Timestamp` header value
   * @param secret - Webhook endpoint secret
   * @param toleranceSeconds - Timestamp tolerance (default: 300)
   */
  verifyWebhookSignature(
    rawBody: string,
    signatureHeader: string,
    timestampHeader: string,
    secret: string,
    toleranceSeconds = 300
  ): Promise<VerifyWebhookSignatureResult> {
    return verifyWebhookSignature({
      payload: rawBody,
      signature: signatureHeader,
      timestamp: timestampHeader,
      secret,
      toleranceSeconds,
    });
  }
}
