import { loadFromRawCategories, type LoadedTerms } from "./loader";

const categoryModules = import.meta.glob("./*.json", {
  eager: true,
  import: "default",
}) as Record<string, unknown>;

function buildRawCategories(): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [path, value] of Object.entries(categoryModules)) {
    const match = path.match(/\.\/(.+)\.json$/);
    if (!match) continue;
    out[match[1]!] = value;
  }
  return out;
}

let cached: LoadedTerms | null = null;

export function loadAllTerms(): LoadedTerms {
  if (cached) return cached;
  cached = loadFromRawCategories(buildRawCategories());
  return cached;
}

export {
  computeCategoryDifficultyCounts,
  computeTermCounts,
  loadFromRawCategories,
  type LoadedTerms,
} from "./loader";
