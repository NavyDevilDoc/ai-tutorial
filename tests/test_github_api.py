"""Tests for GitHub API module."""

import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from core.github_api import create_issue


@pytest.fixture(autouse=True)
def _clear_token_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure GITHUB_TOKEN is cleared before each test."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)


def _mock_response(status: int = 201, body: dict | None = None) -> MagicMock:
    """Create a mock HTTP response."""
    mock = MagicMock()
    mock.read.return_value = json.dumps(
        body or {"html_url": "https://github.com/test/1", "number": 1}
    ).encode("utf-8")
    mock.status = status
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_create_issue_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Successful issue creation should return URL and number."""
    monkeypatch.setenv("GITHUB_TOKEN", "test-token-12345")

    with patch("core.github_api.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _mock_response(
            body={"html_url": "https://github.com/test/issues/42", "number": 42}
        )
        result = create_issue("Test", "Body")

    assert result["html_url"] == "https://github.com/test/issues/42"
    assert result["number"] == 42


def test_create_issue_no_token_raises() -> None:
    """Missing token should raise RuntimeError."""
    with pytest.raises(RuntimeError, match="not configured"):
        create_issue("Test", "Body")


def test_create_issue_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """HTTP errors should raise RuntimeError with status code."""
    monkeypatch.setenv("GITHUB_TOKEN", "test-token-12345")

    with patch("core.github_api.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=422, msg="", hdrs=None, fp=None
        )
        with pytest.raises(RuntimeError, match="status 422"):
            create_issue("Test", "Body")


def test_create_issue_error_does_not_leak_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Error messages must never contain the token value."""
    token = "ghp_SuperSecretToken12345"
    monkeypatch.setenv("GITHUB_TOKEN", token)

    with patch("core.github_api.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=403, msg="", hdrs=None, fp=None
        )
        with pytest.raises(RuntimeError) as exc_info:
            create_issue("Test", "Body")

    assert token not in str(exc_info.value)
    assert "ghp_" not in str(exc_info.value)


def test_create_issue_sends_correct_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The request should include proper Authorization and Content-Type."""
    monkeypatch.setenv("GITHUB_TOKEN", "test-token-12345")

    with patch("core.github_api.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _mock_response()
        create_issue("Test Title", "Test Body", labels=["test-label"])

    request_obj = mock_urlopen.call_args[0][0]
    assert request_obj.get_header("Authorization") == "token test-token-12345"
    assert request_obj.get_header("Content-type") == "application/json"
    assert request_obj.get_header("User-agent") == "ai-tutorial-streamlit"
