/**
 * Counter-based deterministic ID generator for mock server.
 * Produces IDs like: py_test_0001, tx_test_0001, etc.
 */

const counters = new Map<string, number>();

export function generateId(prefix: string): string {
  const current = (counters.get(prefix) ?? 0) + 1;
  counters.set(prefix, current);
  return `${prefix}_test_${String(current).padStart(4, "0")}`;
}

export function resetCounters(): void {
  counters.clear();
}
