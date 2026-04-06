import type { CDPClientConfig } from "../utils/request.js";
import { makeRequest } from "../utils/request.js";

export interface HealthResponse {
  status: "ok" | "degraded";
  mode: "live" | "mock";
  livemode: boolean;
  api_version: string;
  timestamp: string;
}

export interface CapabilitiesResponse {
  version: string;
  api_version: string;
  environments: string[];
  resources: string[];
  payment_rails: string[];
  event_types: string[];
  provenance_link_types: string[];
  idempotency: {
    supported: boolean;
    header_name: string;
  };
  webhooks: {
    supported: boolean;
    signature_algorithm: string;
    signature_header: string;
    timestamp_header: string;
  };
  pagination: {
    default_limit: number;
    max_limit: number;
    cursor_based: boolean;
  };
  sdk_support: {
    typescript: boolean;
    python: boolean;
    mock_server: boolean;
  };
}

export interface VersionResponse {
  api_version: string;
  schema_version: string;
  event_schema_version: string;
  openapi_version: string;
  asyncapi_version: string;
  sdk_versions: Record<string, string>;
  mock_server_version: string;
  generated_at: string;
}

export class CapabilitiesResource {
  constructor(private readonly config: CDPClientConfig) {}

  async get(): Promise<CapabilitiesResponse> {
    return makeRequest(this.config, "GET", "/v1/capabilities");
  }

  async health(): Promise<HealthResponse> {
    return makeRequest(this.config, "GET", "/v1/health");
  }

  async version(): Promise<VersionResponse> {
    return makeRequest(this.config, "GET", "/v1/version");
  }
}
