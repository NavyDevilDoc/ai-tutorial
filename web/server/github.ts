const GITHUB_API_URL = "https://api.github.com";

export interface IssueResult {
  htmlUrl: string;
  number: number;
}

export interface CreateIssueOptions {
  title: string;
  body: string;
  labels?: readonly string[];
  owner?: string;
  repo?: string;
}

function readToken(): string {
  const token = process.env.GITHUB_TOKEN ?? "";
  if (!token) {
    throw new Error(
      "GitHub integration is not configured. Please contact the site administrator.",
    );
  }
  return token;
}

function readRepo(opts: CreateIssueOptions): { owner: string; repo: string } {
  const owner = opts.owner ?? process.env.GITHUB_REPO_OWNER ?? "NavyDevilDoc";
  const repo = opts.repo ?? process.env.GITHUB_REPO_NAME ?? "ai-tutorial";
  return { owner, repo };
}

export async function createIssue(
  opts: CreateIssueOptions,
): Promise<IssueResult> {
  const token = readToken();
  const { owner, repo } = readRepo(opts);

  const url = `${GITHUB_API_URL}/repos/${owner}/${repo}/issues`;
  const payload = {
    title: opts.title,
    body: opts.body,
    labels: opts.labels ?? ["term-suggestion"],
  };

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `token ${token}`,
        Accept: "application/vnd.github.v3+json",
        "User-Agent": "ai-tutorial-react",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error(
      "Could not connect to GitHub. Please check your network connection.",
    );
  }

  if (!response.ok) {
    throw new Error(
      `GitHub API returned status ${response.status}. Please try again later.`,
    );
  }

  const raw = (await response.json()) as { html_url?: string; number?: number };
  return {
    htmlUrl: raw.html_url ?? "",
    number: raw.number ?? 0,
  };
}
