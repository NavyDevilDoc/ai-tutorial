import {
  TermListSchema,
  validateRelatedTerms,
  type Term,
} from "../models";

export interface LoadedTerms {
  bySlug: Map<string, Term>;
  byCategory: Map<string, Term[]>;
}

export function loadFromRawCategories(
  rawByCategory: Record<string, unknown>,
): LoadedTerms {
  const bySlug = new Map<string, Term>();
  const byCategory = new Map<string, Term[]>();

  const categoryKeys = Object.keys(rawByCategory).sort();

  for (const categoryKey of categoryKeys) {
    const parsed = TermListSchema.safeParse(rawByCategory[categoryKey]);
    if (!parsed.success) {
      throw new Error(
        `Invalid term data in '${categoryKey}': ${parsed.error.message}`,
      );
    }
    const terms: Term[] = [];
    for (const term of parsed.data) {
      if (bySlug.has(term.slug)) {
        throw new Error(`Duplicate slug: '${term.slug}'`);
      }
      bySlug.set(term.slug, term);
      terms.push(term);
    }
    byCategory.set(categoryKey, terms);
  }

  const allSlugs: ReadonlySet<string> = new Set(bySlug.keys());
  for (const term of bySlug.values()) {
    validateRelatedTerms(term, allSlugs);
  }

  return { bySlug, byCategory };
}

export function computeTermCounts(loaded: LoadedTerms): {
  byCategory: Record<string, number>;
  byDifficulty: Record<string, number>;
} {
  const byCategory: Record<string, number> = {};
  for (const [key, terms] of loaded.byCategory) {
    byCategory[key] = terms.length;
  }
  const byDifficulty: Record<string, number> = {};
  for (const term of loaded.bySlug.values()) {
    byDifficulty[term.difficulty] = (byDifficulty[term.difficulty] ?? 0) + 1;
  }
  return { byCategory, byDifficulty };
}

export function computeCategoryDifficultyCounts(
  terms: readonly Term[],
): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const term of terms) {
    counts[term.difficulty] = (counts[term.difficulty] ?? 0) + 1;
  }
  return counts;
}
