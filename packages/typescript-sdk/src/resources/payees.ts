import type { CDPClientConfig } from "../utils/request.js";
import { makeRequest } from "../utils/request.js";
import type { PaginationEnvelope, ListParams } from "../types/common.js";
import type {
  Payee,
  CreatePayeeParams,
  PayeeAlias,
  CreatePayeeAliasParams,
  PayoutDestination,
  CreatePayoutDestinationParams,
} from "../types/resources.js";

export class PayeesResource {
  constructor(private readonly config: CDPClientConfig) {}

  async create(
    params: CreatePayeeParams,
    options?: { idempotencyKey?: string }
  ): Promise<Payee> {
    return makeRequest(this.config, "POST", "/v1/payees", {
      body: params,
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async get(payeeId: string): Promise<Payee> {
    return makeRequest(this.config, "GET", `/v1/payees/${payeeId}`);
  }

  async list(params?: ListParams): Promise<PaginationEnvelope<Payee>> {
    return makeRequest(this.config, "GET", "/v1/payees", {
      query: { limit: params?.limit, starting_after: params?.starting_after },
    });
  }

  async update(
    payeeId: string,
    params: Partial<Pick<CreatePayeeParams, "legal_name" | "email" | "default_payout_method" | "metadata">>,
    options?: { idempotencyKey?: string }
  ): Promise<Payee> {
    return makeRequest(this.config, "PATCH", `/v1/payees/${payeeId}`, {
      body: params,
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async createAlias(
    payeeId: string,
    params: CreatePayeeAliasParams,
    options?: { idempotencyKey?: string }
  ): Promise<PayeeAlias> {
    return makeRequest(this.config, "POST", `/v1/payees/${payeeId}/aliases`, {
      body: params,
      idempotencyKey: options?.idempotencyKey,
    });
  }

  async listAliases(
    payeeId: string,
    params?: ListParams
  ): Promise<PaginationEnvelope<PayeeAlias>> {
    return makeRequest(this.config, "GET", `/v1/payees/${payeeId}/aliases`, {
      query: { limit: params?.limit, starting_after: params?.starting_after },
    });
  }

  async createPayoutDestination(
    payeeId: string,
    params: CreatePayoutDestinationParams,
    options?: { idempotencyKey?: string }
  ): Promise<PayoutDestination> {
    return makeRequest(
      this.config,
      "POST",
      `/v1/payees/${payeeId}/payout-destinations`,
      { body: params, idempotencyKey: options?.idempotencyKey }
    );
  }

  async listPayoutDestinations(
    payeeId: string,
    params?: ListParams
  ): Promise<PaginationEnvelope<PayoutDestination>> {
    return makeRequest(
      this.config,
      "GET",
      `/v1/payees/${payeeId}/payout-destinations`,
      { query: { limit: params?.limit, starting_after: params?.starting_after } }
    );
  }
}
