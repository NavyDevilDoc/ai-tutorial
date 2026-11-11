import Fuse, { type IFuseOptions } from "fuse.js";
import type { Term } from "../models";

export const SEARCH_THRESHOLD = 0.4;

interface Candidate {
  slug: string;
  searchable: string;
}

const FUSE_OPTIONS: IFuseOptions<Candidate> = {
  keys: ["searchable"],
  threshold: SEARCH_THRESHOLD,
  ignoreLocation: true,
  includeScore: true,
  minMatchCharLength: 2,
};

function buildCandidates(
  bySlug: ReadonlyMap<string, Term>,
  categoryFilter?: string | null,
): Candidate[] {
  const out: Candidate[] = [];
  for (const term of bySlug.values()) {
    if (categoryFilter && term.category !== categoryFilter) continue;
    out.push({
      slug: term.slug,
      searchable: `${term.term} ${term.tags.join(" ")}`,
    });
  }
  return out;
}

export function searchBestMatch(
  query: string,
  bySlug: ReadonlyMap<string, Term>,
  categoryFilter?: string | null,
): Term | null {
  const trimmed = query.trim();
  if (!trimmed) return null;

  const candidates = buildCandidates(bySlug, categoryFilter);
  if (candidates.length === 0) return null;

  const fuse = new Fuse(candidates, FUSE_OPTIONS);
  const [first] = fuse.search(trimmed, { limit: 1 });
  if (!first) return null;
  return bySlug.get(first.item.slug) ?? null;
}

export function searchSuggestions(
  query: string,
  bySlug: ReadonlyMap<string, Term>,
  limit: number = 5,
  categoryFilter?: string | null,
): Term[] {
  const trimmed = query.trim();
  if (!trimmed) return [];

  const candidates = buildCandidates(bySlug, categoryFilter);
  if (candidates.length === 0) return [];

  const fuse = new Fuse(candidates, FUSE_OPTIONS);
  const results = fuse.search(trimmed, { limit });
  const out: Term[] = [];
  for (const r of results) {
    const term = bySlug.get(r.item.slug);
    if (term) out.push(term);
  }
  return out;
}

export function getAvailableLetters(terms: readonly Term[]): string[] {
  const set = new Set<string>();
  for (const t of terms) {
    if (!t.term) continue;
    set.add(t.term[0]!.toUpperCase());
  }
  return [...set].sort();
}

export function groupTermsByLetter(
  terms: readonly Term[],
): Record<string, Term[]> {
  const groups: Record<string, Term[]> = {};
  for (const t of terms) {
    if (!t.term) continue;
    const letter = t.term[0]!.toUpperCase();
    (groups[letter] ??= []).push(t);
  }
  for (const letter of Object.keys(groups)) {
    groups[letter]!.sort((a, b) => a.term.localeCompare(b.term));
  }
  return groups;
}
