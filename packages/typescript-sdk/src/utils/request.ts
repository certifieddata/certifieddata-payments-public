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
  /** Per-request timeout in ms. Default 30_000. Set to 0 to disable. */
  timeoutMs?: number;
}

const DEFAULT_BASE_URL = "https://api.certifieddata.io";
const DEFAULT_API_VERSION = "2025-01-01";
const DEFAULT_TIMEOUT_MS = 30_000;

export async function makeRequest<T>(
  config: CDPClientConfig,
  method: string,
  path: string,
  options?: {
    body?: unknown;
    query?: Record<string, string | number | undefined>;
    idempotencyKey?: string | undefined;
    /** Per-call timeout override. Falls back to config.timeoutMs, then default. */
    timeoutMs?: number;
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

  const timeoutMs = options?.timeoutMs ?? config.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  const timer = timeoutMs > 0 ? setTimeout(() => controller.abort(), timeoutMs) : null;

  const fetchInit: RequestInit = {
    method,
    headers,
    // Fail loud on cross-origin redirects rather than silently following them.
    // Production responses should never 3xx for an SDK call; if they do, the
    // caller deserves to know.
    redirect: "error",
    signal: controller.signal,
  };
  if (options?.body !== undefined) {
    fetchInit.body = JSON.stringify(options.body);
  }

  let response: Response;
  try {
    response = await fetch(url, fetchInit);
  } catch (err) {
    if ((err as { name?: string }).name === "AbortError") {
      throw new Error(`CDAC request timed out after ${timeoutMs}ms: ${method} ${path}`);
    }
    throw err;
  } finally {
    if (timer) clearTimeout(timer);
  }

  const data: unknown = await response.json();

  if (!response.ok) {
    const errorResponse = data as CDACErrorResponse;
    throw createCDACError(errorResponse.error);
  }

  return data as T;
}
