import { describe, expect, test } from "vitest";
import {
  computeCategoryDifficultyCounts,
  computeTermCounts,
  loadAllTerms,
  loadFromRawCategories,
} from "../data";
import { SAMPLE_TERMS, sampleByCategory, sampleBySlug } from "./fixtures";

const VALID_TEST_CATEGORY = [
  {
    term: "Alpha",
    slug: "alpha",
    category: "test",
    difficulty: "beginner",
    definition: "First term.",
    analogy: "Like the letter A.",
    use_in_a_sentence: "Alpha was loaded first.",
    business_context: "Testing.",
    related_terms: ["beta"],
    tags: ["test"],
  },
  {
    term: "Beta",
    slug: "beta",
    category: "test",
    difficulty: "intermediate",
    definition: "Second term.",
    analogy: "Like the letter B.",
    use_in_a_sentence: "Beta was loaded second.",
    business_context: "Testing.",
    related_terms: ["alpha"],
    tags: ["test"],
  },
];

describe("loadFromRawCategories", () => {
  test("valid data loads with correct lookups", () => {
    const loaded = loadFromRawCategories({ test: VALID_TEST_CATEGORY });
    expect(loaded.bySlug.size).toBe(2);
    expect(loaded.bySlug.has("alpha")).toBe(true);
    expect(loaded.bySlug.has("beta")).toBe(true);
    expect(loaded.byCategory.get("test")?.length).toBe(2);
  });

  test("invalid schema throws", () => {
    const [valid] = VALID_TEST_CATEGORY;
    const bad = { ...valid };
    delete (bad as Record<string, unknown>).analogy;
    expect(() => loadFromRawCategories({ test: [bad] })).toThrow();
  });

  test("dangling related_terms reference throws", () => {
    const lonely = {
      ...VALID_TEST_CATEGORY[0],
      slug: "lonely",
      related_terms: ["nonexistent"],
    };
    expect(() => loadFromRawCategories({ test: [lonely] })).toThrow(
      /nonexistent/,
    );
  });

  test("duplicate slug across categories throws", () => {
    expect(() =>
      loadFromRawCategories({
        cat_a: [VALID_TEST_CATEGORY[0]!],
        cat_b: [VALID_TEST_CATEGORY[0]!],
      }),
    ).toThrow(/Duplicate slug/);
  });
});

describe("computeTermCounts", () => {
  test("per-category counts are correct", () => {
    const loaded = {
      bySlug: sampleBySlug(),
      byCategory: sampleByCategory(),
    };
    const { byCategory } = computeTermCounts(loaded);
    expect(byCategory.test_category).toBe(2);
    expect(byCategory.other_category).toBe(2);
  });

  test("per-difficulty counts are correct", () => {
    const loaded = {
      bySlug: sampleBySlug(),
      byCategory: sampleByCategory(),
    };
    const { byDifficulty } = computeTermCounts(loaded);
    expect(byDifficulty.beginner).toBe(2);
    expect(byDifficulty.intermediate).toBe(1);
    expect(byDifficulty.advanced).toBe(1);
  });
});

describe("computeCategoryDifficultyCounts", () => {
  test("counts a single category correctly", () => {
    const byCat = sampleByCategory();
    const counts = computeCategoryDifficultyCounts(byCat.get("test_category")!);
    expect(counts.beginner).toBe(1);
    expect(counts.intermediate).toBe(1);
    expect(counts.advanced).toBeUndefined();

    const other = computeCategoryDifficultyCounts(
      byCat.get("other_category")!,
    );
    expect(other.advanced).toBe(1);
    expect(other.beginner).toBe(1);
  });
});

describe("loadAllTerms (production data)", () => {
  test("loads production JSON without error", () => {
    const loaded = loadAllTerms();
    expect(loaded.bySlug.size).toBeGreaterThan(0);
    expect(loaded.byCategory.size).toBeGreaterThan(0);
  });

  test("every production slug is URL-safe", () => {
    const loaded = loadAllTerms();
    for (const slug of loaded.bySlug.keys()) {
      expect(slug).toBe(slug.toLowerCase());
      expect(slug).not.toContain(" ");
      for (const ch of slug) {
        const ok = /[a-z0-9-]/.test(ch);
        expect(ok, `slug '${slug}' has invalid char '${ch}'`).toBe(true);
      }
    }
  });

  test("sample reference data is a Term array", () => {
    expect(SAMPLE_TERMS.length).toBeGreaterThan(0);
    expect(SAMPLE_TERMS[0]!.slug).toBe("alpha-term");
  });
});
