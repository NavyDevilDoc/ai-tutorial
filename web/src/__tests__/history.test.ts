import { describe, expect, test } from "vitest";
import { popTermHistory, pushTermHistory } from "../lib/history";

describe("pushTermHistory", () => {
  test("appends a slug to the stack", () => {
    let history = pushTermHistory([], "term-a");
    expect(history).toEqual(["term-a"]);
    history = pushTermHistory(history, "term-b");
    expect(history).toEqual(["term-a", "term-b"]);
  });

  test("respects max_depth by dropping the oldest", () => {
    const history = ["term-0", "term-1", "term-2", "term-3", "term-4"];
    const next = pushTermHistory(history, "new-term", 5);
    expect(next.length).toBe(5);
    expect(next[0]).toBe("term-1");
    expect(next[next.length - 1]).toBe("new-term");
  });

  test("empty-string slug is a noop", () => {
    const history = ["term-a"];
    expect(pushTermHistory(history, "")).toEqual(["term-a"]);
  });

  test("null slug is a noop", () => {
    const history = ["term-a"];
    expect(pushTermHistory(history, null)).toEqual(["term-a"]);
  });

  test("undefined slug is a noop", () => {
    const history = ["term-a"];
    expect(pushTermHistory(history, undefined)).toEqual(["term-a"]);
  });
});

describe("popTermHistory", () => {
  test("returns the most recent slug and shrinks the stack", () => {
    const { slug, remaining } = popTermHistory([
      "term-a",
      "term-b",
      "term-c",
    ]);
    expect(slug).toBe("term-c");
    expect(remaining).toEqual(["term-a", "term-b"]);
  });

  test("returns null and an empty array when the stack is empty", () => {
    const { slug, remaining } = popTermHistory([]);
    expect(slug).toBeNull();
    expect(remaining).toEqual([]);
  });
});
