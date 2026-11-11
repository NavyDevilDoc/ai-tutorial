import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import type { Difficulty } from "../models";
import { DIFFICULTIES } from "../models";

export interface Filters {
  category: string | null;
  difficulty: Difficulty | null;
  letter: string | null;
  query: string;
}

const PARAM_KEYS = {
  category: "category",
  difficulty: "difficulty",
  letter: "letter",
  query: "q",
} as const;

function parseDifficulty(value: string | null): Difficulty | null {
  if (!value) return null;
  return (DIFFICULTIES as readonly string[]).includes(value)
    ? (value as Difficulty)
    : null;
}

function parseLetter(value: string | null): string | null {
  if (!value) return null;
  const upper = value.toUpperCase();
  return /^[A-Z]$/.test(upper) ? upper : null;
}

export function useFilters(): {
  filters: Filters;
  setCategory: (value: string | null) => void;
  setDifficulty: (value: Difficulty | null) => void;
  setLetter: (value: string | null) => void;
  setQuery: (value: string) => void;
  reset: () => void;
} {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useMemo<Filters>(
    () => ({
      category: searchParams.get(PARAM_KEYS.category),
      difficulty: parseDifficulty(searchParams.get(PARAM_KEYS.difficulty)),
      letter: parseLetter(searchParams.get(PARAM_KEYS.letter)),
      query: searchParams.get(PARAM_KEYS.query) ?? "",
    }),
    [searchParams],
  );

  const update = useCallback(
    (key: keyof typeof PARAM_KEYS, value: string | null) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (value && value.length > 0) {
            next.set(PARAM_KEYS[key], value);
          } else {
            next.delete(PARAM_KEYS[key]);
          }
          return next;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  return {
    filters,
    setCategory: (v) => update("category", v),
    setDifficulty: (v) => update("difficulty", v),
    setLetter: (v) => update("letter", v),
    setQuery: (v) => update("query", v),
    reset: () =>
      setSearchParams(() => new URLSearchParams(), { replace: true }),
  };
}

export function filterTerms<T extends { category: string; difficulty: Difficulty; term: string }>(
  terms: readonly T[],
  filters: Pick<Filters, "category" | "difficulty" | "letter">,
): T[] {
  return terms.filter((t) => {
    if (filters.category && t.category !== filters.category) return false;
    if (filters.difficulty && t.difficulty !== filters.difficulty) return false;
    if (
      filters.letter &&
      (t.term[0]?.toUpperCase() ?? "") !== filters.letter
    )
      return false;
    return true;
  });
}
