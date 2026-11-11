import { describe, expect, test } from "vitest";
import {
  getAvailableLetters,
  groupTermsByLetter,
  searchBestMatch,
  searchSuggestions,
} from "../lib/search";
import { SAMPLE_TERMS, sampleBySlug } from "./fixtures";

describe("searchBestMatch", () => {
  test("exact term name returns the correct term", () => {
    const result = searchBestMatch("Alpha Term", sampleBySlug());
    expect(result?.slug).toBe("alpha-term");
  });

  test("partial/typo query still matches the correct term", () => {
    const result = searchBestMatch("Alph Trm", sampleBySlug());
    expect(result?.slug).toBe("alpha-term");
  });

  test("gibberish query returns null", () => {
    const result = searchBestMatch("xyzzy123qqq", sampleBySlug());
    expect(result).toBeNull();
  });

  test("category filter excludes non-matching categories", () => {
    const result = searchBestMatch("Alpha Term", sampleBySlug(), "nonexistent_category");
    expect(result).toBeNull();
  });

  test("tag value finds the term with that tag", () => {
    const result = searchBestMatch("validation", sampleBySlug());
    expect(result?.slug).toBe("beta-term");
  });

  test("empty query returns null", () => {
    expect(searchBestMatch("", sampleBySlug())).toBeNull();
    expect(searchBestMatch("   ", sampleBySlug())).toBeNull();
  });
});

describe("searchSuggestions", () => {
  test("returns one or more matches for a common substring", () => {
    const results = searchSuggestions("term", sampleBySlug(), 5);
    expect(results.length).toBeGreaterThanOrEqual(1);
  });

  test("respects the limit", () => {
    const results = searchSuggestions("term", sampleBySlug(), 2);
    expect(results.length).toBeLessThanOrEqual(2);
  });

  test("empty query returns an empty array", () => {
    expect(searchSuggestions("", sampleBySlug(), 5)).toEqual([]);
  });
});

describe("getAvailableLetters", () => {
  test("returns sorted unique first letters", () => {
    const letters = getAvailableLetters(SAMPLE_TERMS);
    expect(letters).toEqual(["A", "B", "D", "G"]);
  });

  test("empty input returns an empty array", () => {
    expect(getAvailableLetters([])).toEqual([]);
  });
});

describe("groupTermsByLetter", () => {
  test("groups terms by first letter with alphabetical sort within each group", () => {
    const groups = groupTermsByLetter(SAMPLE_TERMS);
    expect(groups.A).toBeDefined();
    expect(groups.A!.length).toBe(1);
    expect(groups.A![0]!.slug).toBe("alpha-term");
    expect(groups.B).toBeDefined();
    expect(groups.D).toBeDefined();
    expect(groups.G).toBeDefined();
    for (const list of Object.values(groups)) {
      const names = list.map((t) => t.term);
      const sorted = [...names].sort();
      expect(names).toEqual(sorted);
    }
  });

  test("empty input returns an empty object", () => {
    expect(groupTermsByLetter([])).toEqual({});
  });
});
