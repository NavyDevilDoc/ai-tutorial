import { describe, expect, test } from "vitest";
import { MAX_PROSE_LENGTH, SuggestionSchema } from "../models";

const MIN = {
  termName: "Fine-tuning",
  category: "nlp",
  difficulty: "beginner" as const,
};

describe("SuggestionSchema", () => {
  test("minimum payload parses with optional fields undefined", () => {
    const result = SuggestionSchema.parse(MIN);
    expect(result.termName).toBe("Fine-tuning");
    expect(result.definition).toBeUndefined();
    expect(result.analogy).toBeUndefined();
    expect(result.use_in_a_sentence).toBeUndefined();
    expect(result.business_context).toBeUndefined();
    expect(result.context).toBeUndefined();
  });

  test("empty-string optional fields are normalized to undefined", () => {
    const result = SuggestionSchema.parse({
      ...MIN,
      context: "",
      definition: "",
      analogy: "",
      use_in_a_sentence: "",
      business_context: "",
    });
    expect(result.context).toBeUndefined();
    expect(result.definition).toBeUndefined();
    expect(result.analogy).toBeUndefined();
  });

  test("whitespace-only optional field trims to undefined", () => {
    const result = SuggestionSchema.parse({ ...MIN, analogy: "   " });
    expect(result.analogy).toBeUndefined();
  });

  test("filled prose fields pass through", () => {
    const result = SuggestionSchema.parse({
      ...MIN,
      definition: "An approximate retrieval.",
      analogy: "Like a librarian.",
    });
    expect(result.definition).toBe("An approximate retrieval.");
    expect(result.analogy).toBe("Like a librarian.");
  });

  test("rejects unknown difficulty", () => {
    expect(() =>
      SuggestionSchema.parse({ ...MIN, difficulty: "expert" }),
    ).toThrow();
  });

  test("rejects category with invalid characters", () => {
    expect(() =>
      SuggestionSchema.parse({ ...MIN, category: "not!a!cat" }),
    ).toThrow();
    expect(() =>
      SuggestionSchema.parse({ ...MIN, category: "Not-A-Cat" }),
    ).toThrow();
  });

  test("rejects empty term name", () => {
    expect(() =>
      SuggestionSchema.parse({ ...MIN, termName: "" }),
    ).toThrow();
    expect(() =>
      SuggestionSchema.parse({ ...MIN, termName: "   " }),
    ).toThrow();
  });

  test("rejects prose fields that exceed MAX_PROSE_LENGTH", () => {
    const tooLong = "a".repeat(MAX_PROSE_LENGTH + 1);
    expect(() =>
      SuggestionSchema.parse({ ...MIN, definition: tooLong }),
    ).toThrow();
  });
});
