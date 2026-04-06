import type { CDPClientConfig } from "../utils/request.js";
import { makeRequest } from "../utils/request.js";
import type { PaginationEnvelope, ListParams } from "../types/common.js";
import type { Refund, CreateRefundParams } from "../types/resources.js";

export class RefundsResource {
  constructor(private readonly config: CDPClientConfig) {}

  async create(
    params: CreateRefundParams,
    options?: { idempotencyKey?: string }
  ): Promise<Refund> {
    return makeRequest(this.config, "POST", "/v1/refunds", {
      body: params,
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async get(refundId: string): Promise<Refund> {
    return makeRequest(this.config, "GET", `/v1/refunds/${refundId}`);
  }

  async list(params?: ListParams): Promise<PaginationEnvelope<Refund>> {
    return makeRequest(this.config, "GET", "/v1/refunds", {
      query: { limit: params?.limit, starting_after: params?.starting_after },
    });
  }
}
