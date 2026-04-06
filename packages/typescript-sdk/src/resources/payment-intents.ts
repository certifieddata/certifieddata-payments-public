import type { CDPClientConfig } from "../utils/request.js";
import { makeRequest } from "../utils/request.js";
import type { PaginationEnvelope, ListParams } from "../types/common.js";
import type { PaymentIntent, CreatePaymentIntentParams } from "../types/resources.js";

export class PaymentIntentsResource {
  constructor(private readonly config: CDPClientConfig) {}

  async create(
    params: CreatePaymentIntentParams,
    options?: { idempotencyKey?: string }
  ): Promise<PaymentIntent> {
    return makeRequest(this.config, "POST", "/v1/payment-intents", {
      body: params,
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async get(intentId: string): Promise<PaymentIntent> {
    return makeRequest(this.config, "GET", `/v1/payment-intents/${intentId}`);
  }

  async list(params?: ListParams): Promise<PaginationEnvelope<PaymentIntent>> {
    return makeRequest(this.config, "GET", "/v1/payment-intents", {
      query: { limit: params?.limit, starting_after: params?.starting_after },
    });
  }

  async confirm(
    intentId: string,
    options?: { idempotencyKey?: string }
  ): Promise<PaymentIntent> {
    return makeRequest(this.config, "POST", `/v1/payment-intents/${intentId}/confirm`, {
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async cancel(
    intentId: string,
    options?: { idempotencyKey?: string }
  ): Promise<PaymentIntent> {
    return makeRequest(this.config, "POST", `/v1/payment-intents/${intentId}/cancel`, {
      idempotencyKey: options?.idempotencyKey,
    });
  }
}
