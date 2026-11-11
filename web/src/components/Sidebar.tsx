import { useEffect, useMemo, useState } from "react";
import {
  ALL_CATEGORIES_LABEL,
  ALL_DIFFICULTIES_LABEL,
  CATEGORY_DISPLAY_NAMES,
  SEARCH_PLACEHOLDER,
} from "../constants";
import { loadAllTerms } from "../data";
import { filterTerms, useFilters } from "../lib/useFilters";
import { useTermNav } from "../lib/useTermNav";
import { cn } from "../lib/utils";
import { getAvailableLetters, searchSuggestions } from "../lib/search";
import type { Difficulty, Term } from "../models";
import { DIFFICULTIES } from "../models";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";

const ALL_SENTINEL = "__all__";

const DIFFICULTY_LABELS: Record<Difficulty, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
};

export function Sidebar() {
  const { goToTerm } = useTermNav();
  const loaded = loadAllTerms();
  const { filters, setCategory, setDifficulty, setLetter, setQuery, reset } =
    useFilters();

  const allTerms = useMemo(
    () => [...loaded.bySlug.values()],
    [loaded],
  );

  const termsAfterCategory = useMemo(
    () => filterTerms(allTerms, { ...filters, letter: null, difficulty: null, category: filters.category }),
    [allTerms, filters],
  );
  const termsAfterCategoryAndDifficulty = useMemo(
    () =>
      filterTerms(termsAfterCategory, {
        category: null,
        letter: null,
        difficulty: filters.difficulty,
      }),
    [termsAfterCategory, filters.difficulty],
  );
  const availableLetters = useMemo(
    () => getAvailableLetters(termsAfterCategoryAndDifficulty),
    [termsAfterCategoryAndDifficulty],
  );
  const browsableTerms = useMemo(
    () =>
      filterTerms(termsAfterCategoryAndDifficulty, {
        category: null,
        difficulty: null,
        letter: filters.letter,
      }).sort((a, b) => a.term.localeCompare(b.term)),
    [termsAfterCategoryAndDifficulty, filters.letter],
  );

  const categoryKeys = useMemo(
    () => [...loaded.byCategory.keys()].sort(),
    [loaded],
  );

  const [localQuery, setLocalQuery] = useState(filters.query);
  useEffect(() => setLocalQuery(filters.query), [filters.query]);

  const suggestions = useMemo<Term[]>(() => {
    if (localQuery.trim().length < 2) return [];
    return searchSuggestions(localQuery, loaded.bySlug, 5, filters.category);
  }, [localQuery, loaded.bySlug, filters.category]);

  function goTo(slug: string) {
    setQuery("");
    setLocalQuery("");
    goToTerm(slug);
  }

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (suggestions[0]) goTo(suggestions[0].slug);
  }

  return (
    <aside className="w-full shrink-0 border-b bg-muted/30 p-6 md:w-80 md:border-b-0 md:border-r">
      <div className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="search-input">Search</Label>
          <form onSubmit={handleSubmit}>
            <Input
              id="search-input"
              value={localQuery}
              onChange={(e) => {
                setLocalQuery(e.target.value);
                setQuery(e.target.value);
              }}
              placeholder={SEARCH_PLACEHOLDER}
              autoComplete="off"
            />
          </form>
          {suggestions.length > 0 && (
            <ul className="mt-1 divide-y rounded-md border text-sm">
              {suggestions.map((t) => (
                <li key={t.slug}>
                  <button
                    type="button"
                    onClick={() => goTo(t.slug)}
                    className="flex w-full items-center justify-between px-3 py-2 text-left hover:bg-accent hover:text-accent-foreground"
                  >
                    <span>{t.term}</span>
                    <span className="text-xs text-muted-foreground">
                      {CATEGORY_DISPLAY_NAMES[t.category] ?? t.category}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="space-y-2">
          <Label>Category</Label>
          <Select
            value={filters.category ?? ALL_SENTINEL}
            onValueChange={(v) =>
              setCategory(v === ALL_SENTINEL ? null : v)
            }
          >
            <SelectTrigger>
              <SelectValue placeholder={ALL_CATEGORIES_LABEL} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ALL_SENTINEL}>
                {ALL_CATEGORIES_LABEL} ({loaded.bySlug.size})
              </SelectItem>
              {categoryKeys.map((key) => {
                const count = loaded.byCategory.get(key)?.length ?? 0;
                return (
                  <SelectItem key={key} value={key}>
                    {CATEGORY_DISPLAY_NAMES[key] ?? key} ({count})
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Difficulty</Label>
          <div className="flex flex-wrap gap-1.5">
            <FilterChip
              active={filters.difficulty === null}
              onClick={() => setDifficulty(null)}
              label={`${ALL_DIFFICULTIES_LABEL} (${termsAfterCategory.length})`}
            />
            {DIFFICULTIES.map((d) => {
              const count = termsAfterCategory.filter(
                (t) => t.difficulty === d,
              ).length;
              return (
                <FilterChip
                  key={d}
                  active={filters.difficulty === d}
                  onClick={() => setDifficulty(d)}
                  label={`${DIFFICULTY_LABELS[d]} (${count})`}
                />
              );
            })}
          </div>
        </div>

        {availableLetters.length > 0 && (
          <div className="space-y-2">
            <Label>Letter</Label>
            <div className="flex flex-wrap gap-1">
              <FilterChip
                active={filters.letter === null}
                onClick={() => setLetter(null)}
                label="All"
              />
              {availableLetters.map((l) => (
                <FilterChip
                  key={l}
                  active={filters.letter === l}
                  onClick={() => setLetter(l)}
                  label={l}
                />
              ))}
            </div>
          </div>
        )}

        {browsableTerms.length > 0 && (
          <div className="space-y-2">
            <Label>Browse ({browsableTerms.length})</Label>
            <Select
              value=""
              onValueChange={(v) => {
                if (v) goTo(v);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Browse terms…" />
              </SelectTrigger>
              <SelectContent>
                {browsableTerms.map((t) => (
                  <SelectItem key={t.slug} value={t.slug}>
                    {t.term}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={reset}
          className="w-full"
        >
          Reset Filters
        </Button>
      </div>
    </aside>
  );
}

function FilterChip({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-md border px-2 py-1 text-xs transition-colors",
        active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-input bg-background hover:bg-accent hover:text-accent-foreground",
      )}
    >
      {label}
    </button>
  );
}
