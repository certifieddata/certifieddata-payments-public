import type { PaginationEnvelope, ListParams } from "../types/common.js";
import type { CDPClientConfig } from "./request.js";
import { makeRequest } from "./request.js";

export async function listAll<T>(
  config: CDPClientConfig,
  path: string,
  params?: ListParams
): Promise<T[]> {
  const results: T[] = [];
  let cursor: string | undefined = params?.starting_after;

  while (true) {
    const page = await makeRequest<PaginationEnvelope<T>>(config, "GET", path, {
      query: {
        limit: params?.limit ?? 100,
        starting_after: cursor,
      },
    });

    results.push(...page.data);

    if (!page.has_more || !page.next_cursor) {
      break;
    }

    cursor = page.next_cursor;
  }

  return results;
}
