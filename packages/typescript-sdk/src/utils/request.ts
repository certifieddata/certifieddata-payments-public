import { createCDACError, type CDACErrorResponse } from "../errors/base.js";

export interface RequestOptions {
  idempotencyKey?: string;
  apiVersion?: string;
}

export interface CDPClientConfig {
  apiKey: string;
  baseUrl: string;
  apiVersion: string;
  idempotencyKey?: string;
}

const DEFAULT_BASE_URL = "https://api.certifieddata.io";
const DEFAULT_API_VERSION = "2025-01-01";

export async function makeRequest<T>(
  config: CDPClientConfig,
  method: string,
  path: string,
  options?: {
    body?: unknown;
    query?: Record<string, string | number | undefined>;
    idempotencyKey?: string | undefined;
  }
): Promise<T> {
  const baseUrl = config.baseUrl ?? DEFAULT_BASE_URL;
  const apiVersion = config.apiVersion ?? DEFAULT_API_VERSION;

  let url = `${baseUrl}${path}`;
  if (options?.query) {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(options.query)) {
      if (value !== undefined) {
        params.set(key, String(value));
      }
    }
    const qs = params.toString();
    if (qs) url += `?${qs}`;
  }

  const headers: Record<string, string> = {
    "Authorization": `Bearer ${config.apiKey}`,
    "CDAC-API-Version": apiVersion,
    "Content-Type": "application/json",
    "Accept": "application/json",
  };

  if (options?.idempotencyKey) {
    headers["Idempotency-Key"] = options.idempotencyKey;
  }

  const fetchInit: RequestInit = { method, headers };
  if (options?.body !== undefined) {
    fetchInit.body = JSON.stringify(options.body);
  }
  const response = await fetch(url, fetchInit);

  const data: unknown = await response.json();

  if (!response.ok) {
    const errorResponse = data as CDACErrorResponse;
    throw createCDACError(errorResponse.error);
  }

  return data as T;
}
