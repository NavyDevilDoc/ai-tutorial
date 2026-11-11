import { describe, expect, test } from "vitest";
import { filterTerms } from "../lib/useFilters";
import { SAMPLE_TERMS } from "./fixtures";

describe("filterTerms", () => {
  test("no filters returns everything", () => {
    const result = filterTerms(SAMPLE_TERMS, {
      category: null,
      difficulty: null,
      letter: null,
    });
    expect(result.length).toBe(SAMPLE_TERMS.length);
  });

  test("category filter narrows the set", () => {
    const result = filterTerms(SAMPLE_TERMS, {
      category: "test_category",
      difficulty: null,
      letter: null,
    });
    expect(result.length).toBe(2);
    expect(result.every((t) => t.category === "test_category")).toBe(true);
  });

  test("difficulty filter narrows the set", () => {
    const result = filterTerms(SAMPLE_TERMS, {
      category: null,
      difficulty: "beginner",
      letter: null,
    });
    expect(result.length).toBe(2);
    expect(result.every((t) => t.difficulty === "beginner")).toBe(true);
  });

  test("letter filter narrows the set", () => {
    const result = filterTerms(SAMPLE_TERMS, {
      category: null,
      difficulty: null,
      letter: "A",
    });
    expect(result.length).toBe(1);
    expect(result[0]?.slug).toBe("alpha-term");
  });

  test("filters compose (category + difficulty)", () => {
    const result = filterTerms(SAMPLE_TERMS, {
      category: "other_category",
      difficulty: "beginner",
      letter: null,
    });
    expect(result.length).toBe(1);
    expect(result[0]?.slug).toBe("delta-term");
  });
});
