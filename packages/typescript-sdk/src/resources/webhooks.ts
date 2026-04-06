import type { CDPClientConfig } from "../utils/request.js";
import { makeRequest } from "../utils/request.js";
import type { PaginationEnvelope, ListParams } from "../types/common.js";
import type { WebhookEndpoint, CreateWebhookEndpointParams } from "../types/resources.js";
import { verifyWebhookSignature } from "../utils/webhooks.js";

export class WebhooksResource {
  constructor(private readonly config: CDPClientConfig) {}

  async create(
    params: CreateWebhookEndpointParams,
    options?: { idempotencyKey?: string }
  ): Promise<WebhookEndpoint> {
    return makeRequest(this.config, "POST", "/v1/webhook-endpoints", {
      body: params,
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async get(webhookEndpointId: string): Promise<WebhookEndpoint> {
    return makeRequest(this.config, "GET", `/v1/webhook-endpoints/${webhookEndpointId}`);
  }

  async list(params?: ListParams): Promise<PaginationEnvelope<WebhookEndpoint>> {
    return makeRequest(this.config, "GET", "/v1/webhook-endpoints", {
      query: { limit: params?.limit, starting_after: params?.starting_after },
    });
  }

  async update(
    webhookEndpointId: string,
    params: Partial<Pick<CreateWebhookEndpointParams, "url" | "enabled_events" | "description">>,
    options?: { idempotencyKey?: string }
  ): Promise<WebhookEndpoint> {
    return makeRequest(this.config, "PATCH", `/v1/webhook-endpoints/${webhookEndpointId}`, {
      body: params,
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async rotateSecret(
    webhookEndpointId: string,
    options?: { idempotencyKey?: string }
  ): Promise<{ secret: string }> {
    return makeRequest(
      this.config,
      "POST",
      `/v1/webhook-endpoints/${webhookEndpointId}/rotate-secret`,
      { idempotencyKey: options?.idempotencyKey }
    );
  }

  async test(
    webhookEndpointId: string,
    params: { event_type: string },
    options?: { idempotencyKey?: string }
  ): Promise<{ delivered: boolean; event_id: string }> {
    return makeRequest(
      this.config,
      "POST",
      `/v1/webhook-endpoints/${webhookEndpointId}/test`,
      { body: params, idempotencyKey: options?.idempotencyKey }
    );
  }

  /**
   * Verify a webhook signature from an incoming CDP webhook request.
   *
   * @param rawBody - The raw request body as a string (before any JSON parsing)
   * @param signatureHeader - Value of the CDP-Signature header (e.g. "t=1712428931,v1=abc...")
   * @param timestampHeader - Value of the CDP-Timestamp header
   * @param secret - Your webhook endpoint secret
   * @param toleranceSeconds - Maximum age of webhook in seconds (default: 300)
   */
  async verifySignature(
    rawBody: string,
    signatureHeader: string,
    timestampHeader: string,
    secret: string,
    toleranceSeconds = 300
  ): Promise<boolean> {
    const result = await verifyWebhookSignature({
      payload: rawBody,
      signature: signatureHeader,
      timestamp: timestampHeader,
      secret,
      toleranceSeconds,
    });
    return result.valid;
  }
}
