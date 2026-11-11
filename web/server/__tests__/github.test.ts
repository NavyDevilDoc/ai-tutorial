import { afterEach, describe, expect, test, vi } from "vitest";
import { createIssue } from "../github";

const ORIGINAL_FETCH = globalThis.fetch;
const ORIGINAL_TOKEN = process.env.GITHUB_TOKEN;

afterEach(() => {
  globalThis.fetch = ORIGINAL_FETCH;
  if (ORIGINAL_TOKEN === undefined) delete process.env.GITHUB_TOKEN;
  else process.env.GITHUB_TOKEN = ORIGINAL_TOKEN;
  vi.restoreAllMocks();
});

describe("createIssue", () => {
  test("posts to the correct URL with token header and returns issue info", async () => {
    process.env.GITHUB_TOKEN = "secret-token-xyz";
    process.env.GITHUB_REPO_OWNER = "TestOwner";
    process.env.GITHUB_REPO_NAME = "test-repo";

    const fetchMock = vi.fn<typeof fetch>(
      async () =>
        new Response(
          JSON.stringify({ html_url: "https://example.test/42", number: 42 }),
          { status: 201 },
        ),
    );
    globalThis.fetch = fetchMock;

    const result = await createIssue({ title: "T", body: "B" });

    expect(fetchMock).toHaveBeenCalledOnce();
    const call = fetchMock.mock.calls[0];
    expect(call).toBeDefined();
    const [url, init] = call!;
    expect(url).toBe("https://api.github.com/repos/TestOwner/test-repo/issues");
    expect(init).toBeDefined();
    expect(init!.method).toBe("POST");
    const headers = init!.headers as Record<string, string>;
    expect(headers.Authorization).toBe("token secret-token-xyz");
    expect(headers["Content-Type"]).toBe("application/json");
    expect(result.htmlUrl).toBe("https://example.test/42");
    expect(result.number).toBe(42);
  });

  test("throws when no token is configured", async () => {
    delete process.env.GITHUB_TOKEN;
    await expect(createIssue({ title: "T", body: "B" })).rejects.toThrow(
      /not configured/,
    );
  });

  test("error messages never leak the token", async () => {
    process.env.GITHUB_TOKEN = "SECRET-123";
    const fetchMock = vi.fn(
      async () =>
        new Response(JSON.stringify({ message: "bad creds" }), {
          status: 401,
        }),
    );
    globalThis.fetch = fetchMock as unknown as typeof fetch;

    await expect(createIssue({ title: "T", body: "B" })).rejects.toThrow(
      /GitHub API returned status 401/,
    );
    try {
      await createIssue({ title: "T", body: "B" });
    } catch (e) {
      expect((e as Error).message).not.toContain("SECRET-123");
    }
  });

  test("network failure produces a friendly message", async () => {
    process.env.GITHUB_TOKEN = "t";
    globalThis.fetch = (() => {
      throw new TypeError("network fail");
    }) as unknown as typeof fetch;
    await expect(createIssue({ title: "T", body: "B" })).rejects.toThrow(
      /Could not connect/,
    );
  });
});
