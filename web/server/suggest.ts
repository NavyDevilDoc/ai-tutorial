import { Hono } from "hono";
import {
  buildIssueBody,
  sanitizeContext,
  sanitizeProse,
  sanitizeTermName,
  type IssuePayload,
} from "../src/lib/sanitize";
import { SuggestionSchema } from "../src/models";
import { createIssue } from "./github";
import { createRateLimiter, type RateLimiter } from "./rateLimit";

function clientIp(c: {
  req: {
    header: (name: string) => string | undefined;
    raw: { headers: Headers };
  };
}): string {
  const forwarded = c.req.header("x-forwarded-for");
  if (forwarded) return forwarded.split(",")[0]!.trim();
  const real = c.req.header("x-real-ip");
  if (real) return real.trim();
  return "unknown";
}

export interface SuggestRouterOptions {
  limiter?: RateLimiter;
  createIssueImpl?: typeof createIssue;
}

export function createSuggestRouter(options: SuggestRouterOptions = {}) {
  const limiter =
    options.limiter ??
    createRateLimiter({ windowMs: 60 * 60 * 1000, max: 3 });
  const createIssueFn = options.createIssueImpl ?? createIssue;

  const app = new Hono();

  app.post("/suggest", async (c) => {
    const ip = clientIp(c);
    const rate = limiter.check(ip);
    if (!rate.allowed) {
      return c.json(
        {
          error:
            "You've already submitted several suggestions recently. Please try again later.",
        },
        429,
        { "Retry-After": String(rate.retryAfterSec) },
      );
    }

    let rawBody: unknown;
    try {
      rawBody = await c.req.json();
    } catch {
      return c.json({ error: "Invalid JSON body." }, 400);
    }

    const parsed = SuggestionSchema.safeParse(rawBody);
    if (!parsed.success) {
      const first = parsed.error.issues[0];
      const path = first?.path.join(".") ?? "input";
      return c.json(
        { error: `Invalid ${path}: ${first?.message ?? "validation failed"}` },
        400,
      );
    }
    const data = parsed.data;

    let cleanedName: string;
    try {
      cleanedName = sanitizeTermName(data.termName);
    } catch {
      return c.json(
        { error: "Term name is empty or invalid after sanitization." },
        400,
      );
    }

    const payload: IssuePayload = {
      termName: cleanedName,
      category: data.category,
      difficulty: data.difficulty,
    };
    if (data.context) payload.context = sanitizeContext(data.context);
    if (data.definition) payload.definition = sanitizeProse(data.definition);
    if (data.analogy) payload.analogy = sanitizeProse(data.analogy);
    if (data.use_in_a_sentence)
      payload.use_in_a_sentence = sanitizeProse(data.use_in_a_sentence);
    if (data.business_context)
      payload.business_context = sanitizeProse(data.business_context);

    const title = `Suggested term: ${cleanedName}`;
    const bodyMd = buildIssueBody(payload);

    try {
      const issue = await createIssueFn({ title, body: bodyMd });
      return c.json({ issueUrl: issue.htmlUrl, issueNumber: issue.number });
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Unknown error submitting issue.";
      return c.json({ error: msg }, 502);
    }
  });

  return app;
}
