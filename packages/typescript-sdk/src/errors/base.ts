export interface CDACErrorResponse {
  error: {
    code: string;
    message: string;
    http_status: number;
    retryable: boolean;
    docs_url?: string;
    validation_errors?: Array<{ field: string; message: string }>;
  };
}

export class CDACError extends Error {
  readonly code: string;
  readonly httpStatus: number;
  readonly retryable: boolean;
  readonly docsUrl?: string;
  readonly validationErrors?: Array<{ field: string; message: string }>;

  constructor(response: CDACErrorResponse["error"]) {
    super(response.message);
    this.name = "CDACError";
    this.code = response.code;
    this.httpStatus = response.http_status;
    this.retryable = response.retryable;
    if (response.docs_url !== undefined) this.docsUrl = response.docs_url;
    if (response.validation_errors !== undefined) this.validationErrors = response.validation_errors;
  }
}

export class CDACAuthError extends CDACError {
  constructor(response: CDACErrorResponse["error"]) {
    super(response);
    this.name = "CDACAuthError";
  }
}

export class CDACValidationError extends CDACError {
  constructor(response: CDACErrorResponse["error"]) {
    super(response);
    this.name = "CDACValidationError";
  }
}

export class CDACNotFoundError extends CDACError {
  constructor(response: CDACErrorResponse["error"]) {
    super(response);
    this.name = "CDACNotFoundError";
  }
}

export class CDACConflictError extends CDACError {
  constructor(response: CDACErrorResponse["error"]) {
    super(response);
    this.name = "CDACConflictError";
  }
}

export class CDACRateLimitError extends CDACError {
  constructor(response: CDACErrorResponse["error"]) {
    super(response);
    this.name = "CDACRateLimitError";
  }
}

export function createCDACError(response: CDACErrorResponse["error"]): CDACError {
  if (response.http_status === 401 || response.http_status === 403) {
    return new CDACAuthError(response);
  }
  if (response.http_status === 400 && response.code.startsWith("validation.")) {
    return new CDACValidationError(response);
  }
  if (response.http_status === 404) {
    return new CDACNotFoundError(response);
  }
  if (response.http_status === 409) {
    return new CDACConflictError(response);
  }
  if (response.http_status === 429) {
    return new CDACRateLimitError(response);
  }
  return new CDACError(response);
}
