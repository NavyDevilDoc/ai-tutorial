import { MAX_HISTORY_DEPTH } from "../constants";

export function pushTermHistory(
  history: readonly string[],
  slug: string | null | undefined,
  maxDepth: number = MAX_HISTORY_DEPTH,
): string[] {
  if (!slug) return [...history];
  const next = [...history, slug];
  if (next.length > maxDepth) {
    return next.slice(next.length - maxDepth);
  }
  return next;
}

export function popTermHistory(
  history: readonly string[],
): { slug: string | null; remaining: string[] } {
  if (history.length === 0) {
    return { slug: null, remaining: [] };
  }
  return {
    slug: history[history.length - 1]!,
    remaining: history.slice(0, -1),
  };
}
