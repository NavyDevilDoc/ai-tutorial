import { describe, expect, test } from "vitest";
import { createSuggestRouter } from "../suggest";
import { createRateLimiter } from "../rateLimit";
import type { IssueResult } from "../github";

function makeApp(overrides: {
  createIssue?: () => Promise<IssueResult>;
  max?: number;
  windowMs?: number;
} = {}) {
  const createIssueImpl =
    overrides.createIssue ??
    (async () => ({ htmlUrl: "https://example.test/1", number: 1 }));
  const limiter = createRateLimiter({
    windowMs: overrides.windowMs ?? 60_000,
    max: overrides.max ?? 3,
  });
  return createSuggestRouter({
    createIssueImpl: createIssueImpl as never,
    limiter,
  });
}

const GOOD_PAYLOAD = {
  termName: "Fine-tuning",
  category: "nlp",
  difficulty: "beginner",
  context: "heard it in standup",
};

async function post(
  app: ReturnType<typeof createSuggestRouter>,
  body: unknown,
  headers: Record<string, string> = {},
) {
  return app.request("/suggest", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
}

describe("POST /suggest", () => {
  test("happy path returns 200 with issueUrl + issueNumber", async () => {
    const app = makeApp();
    const res = await post(app, GOOD_PAYLOAD);
    expect(res.status).toBe(200);
    const data = (await res.json()) as {
      issueUrl: string;
      issueNumber: number;
    };
    expect(data.issueUrl).toBe("https://example.test/1");
    expect(data.issueNumber).toBe(1);
  });

  test("rejects missing term name", async () => {
    const app = makeApp();
    const res = await post(app, { ...GOOD_PAYLOAD, termName: undefined });
    expect(res.status).toBe(400);
  });

  test("rejects invalid category", async () => {
    const app = makeApp();
    const res = await post(app, {
      ...GOOD_PAYLOAD,
      category: "not!a!cat",
    });
    expect(res.status).toBe(400);
  });

  test("rejects invalid difficulty", async () => {
    const app = makeApp();
    const res = await post(app, { ...GOOD_PAYLOAD, difficulty: "expert" });
    expect(res.status).toBe(400);
  });

  test("rejects term names that sanitize to empty", async () => {
    const app = makeApp();
    const res = await post(app, { ...GOOD_PAYLOAD, termName: "<<<>>>" });
    expect(res.status).toBe(400);
  });

  test("returns 429 after rate limit exhausted (per IP)", async () => {
    const app = makeApp({ max: 2, windowMs: 60_000 });
    const headers = { "x-forwarded-for": "10.0.0.5" };
    const first = await post(app, GOOD_PAYLOAD, headers);
    const second = await post(app, GOOD_PAYLOAD, headers);
    const third = await post(app, GOOD_PAYLOAD, headers);
    expect(first.status).toBe(200);
    expect(second.status).toBe(200);
    expect(third.status).toBe(429);
  });

  test("separate IPs get their own buckets", async () => {
    const app = makeApp({ max: 1, windowMs: 60_000 });
    const a = await post(app, GOOD_PAYLOAD, { "x-forwarded-for": "1.1.1.1" });
    const b = await post(app, GOOD_PAYLOAD, { "x-forwarded-for": "2.2.2.2" });
    expect(a.status).toBe(200);
    expect(b.status).toBe(200);
  });

  test("returns 502 when createIssue throws", async () => {
    const app = makeApp({
      createIssue: async () => {
        throw new Error("GitHub API returned status 503. Please try again later.");
      },
    });
    const res = await post(app, GOOD_PAYLOAD);
    expect(res.status).toBe(502);
    const data = (await res.json()) as { error: string };
    expect(data.error).toMatch(/503/);
  });

  test("user-provided prose fields flow through to the issue body JSON", async () => {
    const seen: { title?: string; body?: string } = {};
    const app = makeApp({
      createIssue: (async (opts: { title: string; body: string }) => {
        seen.title = opts.title;
        seen.body = opts.body;
        return { htmlUrl: "https://example.test/9", number: 9 };
      }) as never,
    });
    const res = await post(app, {
      ...GOOD_PAYLOAD,
      definition: "An approximate retrieval of nearest matches.",
      analogy: "Like asking a librarian.",
      use_in_a_sentence: "We used embeddings to search for similar docs.",
      business_context: "Powers in-product semantic search.",
    });
    expect(res.status).toBe(200);
    expect(seen.body).toBeDefined();
    const start = seen.body!.indexOf("```json\n") + "```json\n".length;
    const end = seen.body!.indexOf("\n```", start);
    const parsed = JSON.parse(seen.body!.slice(start, end)) as Record<
      string,
      string
    >;
    expect(parsed.definition).toMatch(/nearest matches/);
    expect(parsed.analogy).toMatch(/librarian/);
    expect(parsed.use_in_a_sentence).toMatch(/embeddings/);
    expect(parsed.business_context).toMatch(/semantic search/);
  });

  test("omits optional prose from issue body when not provided", async () => {
    const seen: { body?: string } = {};
    const app = makeApp({
      createIssue: (async (opts: { body: string }) => {
        seen.body = opts.body;
        return { htmlUrl: "https://example.test/10", number: 10 };
      }) as never,
    });
    const res = await post(app, {
      termName: "Compute",
      category: "ml_fundamentals",
      difficulty: "beginner",
    });
    expect(res.status).toBe(200);
    expect(seen.body).toContain("None provided.");
    const start = seen.body!.indexOf("```json\n") + "```json\n".length;
    const end = seen.body!.indexOf("\n```", start);
    const parsed = JSON.parse(seen.body!.slice(start, end)) as Record<
      string,
      unknown
    >;
    expect(parsed.definition).toBeUndefined();
    expect(parsed.analogy).toBeUndefined();
  });
});

describe("rate limiter", () => {
  test("resets after window expires", () => {
    let now = 1000;
    const limiter = createRateLimiter({
      windowMs: 1000,
      max: 1,
      now: () => now,
    });
    expect(limiter.check("k").allowed).toBe(true);
    expect(limiter.check("k").allowed).toBe(false);
    now = 2500;
    expect(limiter.check("k").allowed).toBe(true);
  });

  test("retryAfterSec is positive when blocked", () => {
    let now = 0;
    const limiter = createRateLimiter({
      windowMs: 10_000,
      max: 1,
      now: () => now,
    });
    limiter.check("k");
    const blocked = limiter.check("k");
    expect(blocked.allowed).toBe(false);
    expect(blocked.retryAfterSec).toBeGreaterThan(0);
  });
});
