import type { CDPClientConfig } from "../utils/request.js";
import { makeRequest } from "../utils/request.js";
import type { PaginationEnvelope, ListParams, ProvenanceLinkSet } from "../types/common.js";
import type { Transaction, CreateTransactionParams } from "../types/resources.js";

export class TransactionsResource {
  constructor(private readonly config: CDPClientConfig) {}

  async create(
    params: CreateTransactionParams,
    options?: { idempotencyKey?: string }
  ): Promise<Transaction> {
    return makeRequest(this.config, "POST", "/v1/transactions", {
      body: params,
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async get(transactionId: string): Promise<Transaction> {
    return makeRequest(this.config, "GET", `/v1/transactions/${transactionId}`);
  }

  async list(params?: ListParams): Promise<PaginationEnvelope<Transaction>> {
    return makeRequest(this.config, "GET", "/v1/transactions", {
      query: { limit: params?.limit, starting_after: params?.starting_after },
    });
  }

  /**
   * Attach provenance links to a transaction.
   *
   * Links are mutable until status = captured. After capture, they are immutable
   * and this endpoint returns 409 (provenance.immutable_after_capture).
   *
   * @see test-vectors/provenance/attach-before-capture.valid.json
   */
  async attachLinks(
    transactionId: string,
    links: ProvenanceLinkSet,
    options?: { idempotencyKey?: string }
  ): Promise<Transaction> {
    return makeRequest(
      this.config,
      "POST",
      `/v1/transactions/${transactionId}/attach-links`,
      { body: links, idempotencyKey: options?.idempotencyKey }
    );
  }

  async capture(
    transactionId: string,
    options?: { idempotencyKey?: string }
  ): Promise<Transaction> {
    return makeRequest(
      this.config,
      "POST",
      `/v1/transactions/${transactionId}/capture`,
      { idempotencyKey: options?.idempotencyKey }
    );
  }

  async cancel(
    transactionId: string,
    options?: { idempotencyKey?: string }
  ): Promise<Transaction> {
    return makeRequest(
      this.config,
      "POST",
      `/v1/transactions/${transactionId}/cancel`,
      { idempotencyKey: options?.idempotencyKey }
    );
  }
}
