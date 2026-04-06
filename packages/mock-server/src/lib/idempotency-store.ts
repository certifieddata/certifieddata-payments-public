/**
 * In-memory idempotency store.
 * Keys are retained for the session only (no persistence).
 */

interface IdempotencyRecord {
  status: number;
  body: unknown;
  created_at: number;
}

const TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

const store = new Map<string, IdempotencyRecord>();

export function getIdempotencyRecord(key: string): IdempotencyRecord | undefined {
  const record = store.get(key);
  if (!record) return undefined;
  if (Date.now() - record.created_at > TTL_MS) {
    store.delete(key);
    return undefined;
  }
  return record;
}

export function setIdempotencyRecord(key: string, status: number, body: unknown): void {
  store.set(key, { status, body, created_at: Date.now() });
}

export function clearIdempotencyStore(): void {
  store.clear();
}
