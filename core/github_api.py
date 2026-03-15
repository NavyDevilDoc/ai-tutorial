"""GitHub API client for creating issues.

Uses urllib (stdlib) to avoid adding runtime dependencies.
The GitHub token is read from environment variables and never
logged, printed, or included in error messages.
"""

import json
import os
import urllib.error
import urllib.request

GITHUB_API_URL: str = "https://api.github.com"
REPO_OWNER: str = "NavyDevilDoc"
REPO_NAME: str = "ai-tutorial"


def _get_token() -> str:
    """Read the GitHub token from the environment.

    Returns:
        The token string.

    Raises:
        RuntimeError: If no token is configured.
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError(
            "GitHub integration is not configured. "
            "Please contact the site administrator."
        )
    return token


def create_issue(
    title: str,
    body: str,
    labels: list[str] | None = None,
) -> dict:
    """Create a GitHub Issue via the REST API.

    Args:
        title: Issue title.
        body: Issue body (markdown).
        labels: Optional list of label names.

    Returns:
        Dict with 'html_url' and 'number' of the created issue.

    Raises:
        RuntimeError: If the token is missing or the API call fails.
    """
    token = _get_token()

    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    payload = json.dumps({
        "title": title,
        "body": body,
        "labels": labels or ["term-suggestion"],
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ai-tutorial-streamlit",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))
            return {
                "html_url": result.get("html_url", ""),
                "number": result.get("number", 0),
            }
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"GitHub API returned status {exc.code}. "
            "Please try again later."
        ) from None
    except urllib.error.URLError:
        raise RuntimeError(
            "Could not connect to GitHub. "
            "Please check your network connection."
        ) from None
