import type { CDPClientConfig } from "../utils/request.js";
import { makeRequest } from "../utils/request.js";
import type { PaginationEnvelope, ListParams } from "../types/common.js";
import type { Settlement, CreateSettlementParams } from "../types/resources.js";

export class SettlementsResource {
  constructor(private readonly config: CDPClientConfig) {}

  async create(
    params: CreateSettlementParams,
    options?: { idempotencyKey?: string }
  ): Promise<Settlement> {
    return makeRequest(this.config, "POST", "/v1/settlements", {
      body: params,
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async get(settlementId: string): Promise<Settlement> {
    return makeRequest(this.config, "GET", `/v1/settlements/${settlementId}`);
  }

  async list(params?: ListParams): Promise<PaginationEnvelope<Settlement>> {
    return makeRequest(this.config, "GET", "/v1/settlements", {
      query: { limit: params?.limit, starting_after: params?.starting_after },
    });
  }

  async submit(
    settlementId: string,
    options?: { idempotencyKey?: string }
  ): Promise<Settlement> {
    return makeRequest(this.config, "POST", `/v1/settlements/${settlementId}/submit`, {
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async cancel(
    settlementId: string,
    options?: { idempotencyKey?: string }
  ): Promise<Settlement> {
    return makeRequest(this.config, "POST", `/v1/settlements/${settlementId}/cancel`, {
      idempotencyKey: options?.idempotencyKey,
    });
  }
}
