import { describe, expect, test } from "vitest";
import { TermSchema, validateRelatedTerms, type Term } from "../models";
import { VALID_TERM_DATA } from "./fixtures";

describe("TermSchema", () => {
  test("valid term parses successfully", () => {
    const term = TermSchema.parse(VALID_TERM_DATA);
    expect(term.slug).toBe("test-term");
    expect(term.difficulty).toBe("beginner");
  });

  test("missing required field fails validation", () => {
    const required = [
      "term",
      "slug",
      "definition",
      "analogy",
      "use_in_a_sentence",
    ] as const;
    for (const field of required) {
      const data: Record<string, unknown> = { ...VALID_TERM_DATA };
      delete data[field];
      expect(() => TermSchema.parse(data)).toThrow();
    }
  });

  test("invalid difficulty fails validation", () => {
    expect(() =>
      TermSchema.parse({ ...VALID_TERM_DATA, difficulty: "expert" }),
    ).toThrow();
  });

  test("invalid slug formats fail validation", () => {
    for (const bad of ["Test-Term", "test term", "TEST", "test_term"]) {
      expect(() =>
        TermSchema.parse({ ...VALID_TERM_DATA, slug: bad }),
      ).toThrow();
    }
  });

  test("valid slug formats pass validation", () => {
    for (const good of ["test", "test-term", "a-b-c", "ml101"]) {
      const term = TermSchema.parse({ ...VALID_TERM_DATA, slug: good });
      expect(term.slug).toBe(good);
    }
  });
});

describe("validateRelatedTerms", () => {
  test("passes when all referenced slugs exist", () => {
    const term: Term = TermSchema.parse({
      ...VALID_TERM_DATA,
      related_terms: ["other-term"],
    });
    expect(() =>
      validateRelatedTerms(term, new Set(["test-term", "other-term"])),
    ).not.toThrow();
  });

  test("throws on dangling slug reference", () => {
    const term: Term = TermSchema.parse({
      ...VALID_TERM_DATA,
      related_terms: ["nonexistent"],
    });
    expect(() =>
      validateRelatedTerms(term, new Set(["test-term"])),
    ).toThrow(/nonexistent/);
  });
});
