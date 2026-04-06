export interface CDPErrorResponse {
  error: {
    code: string;
    message: string;
    http_status: number;
    retryable: boolean;
    docs_url?: string;
    validation_errors?: Array<{ field: string; message: string }>;
  };
}

export class CDPError extends Error {
  readonly code: string;
  readonly httpStatus: number;
  readonly retryable: boolean;
  readonly docsUrl?: string;
  readonly validationErrors?: Array<{ field: string; message: string }>;

  constructor(response: CDPErrorResponse["error"]) {
    super(response.message);
    this.name = "CDPError";
    this.code = response.code;
    this.httpStatus = response.http_status;
    this.retryable = response.retryable;
    if (response.docs_url !== undefined) this.docsUrl = response.docs_url;
    if (response.validation_errors !== undefined) this.validationErrors = response.validation_errors;
  }
}

export class CDPAuthError extends CDPError {
  constructor(response: CDPErrorResponse["error"]) {
    super(response);
    this.name = "CDPAuthError";
  }
}

export class CDPValidationError extends CDPError {
  constructor(response: CDPErrorResponse["error"]) {
    super(response);
    this.name = "CDPValidationError";
  }
}

export class CDPNotFoundError extends CDPError {
  constructor(response: CDPErrorResponse["error"]) {
    super(response);
    this.name = "CDPNotFoundError";
  }
}

export class CDPConflictError extends CDPError {
  constructor(response: CDPErrorResponse["error"]) {
    super(response);
    this.name = "CDPConflictError";
  }
}

export class CDPRateLimitError extends CDPError {
  constructor(response: CDPErrorResponse["error"]) {
    super(response);
    this.name = "CDPRateLimitError";
  }
}

export function createCDPError(response: CDPErrorResponse["error"]): CDPError {
  if (response.http_status === 401 || response.http_status === 403) {
    return new CDPAuthError(response);
  }
  if (response.http_status === 400 && response.code.startsWith("validation.")) {
    return new CDPValidationError(response);
  }
  if (response.http_status === 404) {
    return new CDPNotFoundError(response);
  }
  if (response.http_status === 409) {
    return new CDPConflictError(response);
  }
  if (response.http_status === 429) {
    return new CDPRateLimitError(response);
  }
  return new CDPError(response);
}
