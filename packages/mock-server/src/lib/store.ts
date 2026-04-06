/**
 * Simple in-memory resource store for all mock server resources.
 */

const stores = new Map<string, Map<string, unknown>>();

function getStore(resource: string): Map<string, unknown> {
  if (!stores.has(resource)) stores.set(resource, new Map());
  return stores.get(resource)!;
}

export function saveResource<T extends { id: string }>(resource: string, obj: T): T {
  getStore(resource).set(obj.id, obj);
  return obj;
}

export function getResource<T>(resource: string, id: string): T | undefined {
  return getStore(resource).get(id) as T | undefined;
}

export function listResources<T>(
  resource: string,
  params?: { limit?: number; starting_after?: string; filter?: (item: T) => boolean }
): { data: T[]; has_more: boolean; next_cursor: string | null } {
  const all = [...getStore(resource).values()] as T[];
  const limit = Math.min(params?.limit ?? 20, 100);

  let items = params?.filter ? all.filter(params.filter) : all;

  if (params?.starting_after) {
    const idx = items.findIndex((item) => (item as { id: string }).id === params.starting_after);
    if (idx !== -1) items = items.slice(idx + 1);
  }

  const page = items.slice(0, limit);
  const has_more = items.length > limit;
  return {
    data: page,
    has_more,
    next_cursor: has_more ? (page[page.length - 1] as { id: string }).id : null,
  };
}

export function updateResource<T extends { id: string }>(
  resource: string,
  id: string,
  updates: Partial<T>
): T | undefined {
  const store = getStore(resource);
  const existing = store.get(id) as T | undefined;
  if (!existing) return undefined;
  const updated = { ...existing, ...updates, updated_at: new Date().toISOString() };
  store.set(id, updated);
  return updated as T;
}

export function clearAllStores(): void {
  stores.clear();
}
