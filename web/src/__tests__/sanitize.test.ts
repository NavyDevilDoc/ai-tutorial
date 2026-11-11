import { describe, expect, test } from "vitest";
import {
  buildIssueBody,
  sanitizeContext,
  sanitizeTermName,
  sanitizeText,
} from "../lib/sanitize";

describe("sanitizeText", () => {
  test("strips leading and trailing whitespace", () => {
    expect(sanitizeText("  hello  ")).toBe("hello");
  });

  test("truncates to max_length", () => {
    const result = sanitizeText("a".repeat(200), 50);
    expect(result.length).toBe(50);
  });

  test("removes null bytes", () => {
    expect(sanitizeText("hel\x00lo")).toBe("hello");
  });

  test("replaces control chars with spaces (preserves newline)", () => {
    expect(sanitizeText("hello\x01world\x0etest")).toBe("hello world test");
  });

  test("preserves newlines in context text", () => {
    expect(sanitizeText("line1\nline2")).toBe("line1\nline2");
  });
});

describe("sanitizeTermName", () => {
  test("passes through normal term names", () => {
    expect(sanitizeTermName("Supervised Learning")).toBe("Supervised Learning");
    expect(sanitizeTermName("K-Nearest Neighbors")).toBe(
      "K-Nearest Neighbors",
    );
    expect(sanitizeTermName("A/B Testing")).toBe("A/B Testing");
  });

  test("strips HTML angle brackets", () => {
    const result = sanitizeTermName("<script>alert(1)</script>Compute");
    expect(result).not.toContain("<");
    expect(result).not.toContain(">");
    expect(result).toContain("Compute");
  });

  test("throws when sanitization yields an empty string", () => {
    expect(() => sanitizeTermName("   <>><<>  ")).toThrow(/empty/);
  });
});

describe("sanitizeContext", () => {
  test("preserves common punctuation", () => {
    const text = "This is useful for NLP tasks, e.g. sentiment analysis.";
    expect(sanitizeContext(text)).toBe(text);
  });
});

describe("buildIssueBody", () => {
  function extractJson(body: string): Record<string, unknown> {
    const start = body.indexOf("```json\n") + "```json\n".length;
    const end = body.indexOf("\n```", start);
    return JSON.parse(body.slice(start, end));
  }

  test("contains a JSON code block with the structured data", () => {
    const body = buildIssueBody({
      termName: "Compute",
      category: "ml_fundamentals",
      difficulty: "beginner",
      context: "Test context",
    });
    expect(body).toContain("```json");
    expect(body).toContain("```");
    const parsed = extractJson(body);
    expect(parsed.term_name).toBe("Compute");
    expect(parsed.category).toBe("ml_fundamentals");
    expect(parsed.context).toBe("Test context");
  });

  test("escapes quotes via JSON serialization", () => {
    const body = buildIssueBody({
      termName: "Bayes' Theorem",
      category: "statistics",
      difficulty: "intermediate",
    });
    const parsed = extractJson(body);
    expect(parsed.term_name).toBe("Bayes' Theorem");
  });

  test("omits optional prose fields when empty", () => {
    const body = buildIssueBody({
      termName: "X",
      category: "nlp",
      difficulty: "beginner",
    });
    const parsed = extractJson(body);
    expect(parsed.definition).toBeUndefined();
    expect(parsed.analogy).toBeUndefined();
    expect(parsed.use_in_a_sentence).toBeUndefined();
    expect(parsed.business_context).toBeUndefined();
    expect(body).toContain("None provided.");
  });

  test("includes user-provided prose fields under snake_case keys", () => {
    const body = buildIssueBody({
      termName: "Autoencoder",
      category: "neural_networks",
      difficulty: "advanced",
      definition: "A neural network that learns to compress and reconstruct.",
      analogy: "Like a book summary.",
      use_in_a_sentence: "We trained an autoencoder on transactions.",
      business_context: "Used in fraud detection.",
    });
    const parsed = extractJson(body);
    expect(parsed.definition).toMatch(/compress/);
    expect(parsed.analogy).toMatch(/book/);
    expect(parsed.use_in_a_sentence).toMatch(/transactions/);
    expect(parsed.business_context).toMatch(/fraud/);
    // Human-readable markdown sections too
    expect(body).toMatch(/### Definition\n\nA neural network/);
    expect(body).toMatch(/### Analogy\n\nLike a book/);
  });
});
