"""Tests for input sanitization layer."""

import json

import pytest

from core.sanitize import (
    build_issue_body,
    sanitize_context,
    sanitize_term_name,
    sanitize_text,
)


def test_sanitize_text_strips_whitespace() -> None:
    """Leading and trailing whitespace should be removed."""
    assert sanitize_text("  hello  ") == "hello"


def test_sanitize_text_truncates() -> None:
    """Strings longer than max_length should be truncated."""
    result = sanitize_text("a" * 200, max_length=50)
    assert len(result) == 50


def test_sanitize_text_removes_null_bytes() -> None:
    """Null bytes should be stripped."""
    assert sanitize_text("hel\x00lo") == "hello"


def test_sanitize_text_replaces_control_chars() -> None:
    """Control characters (except newline) should become spaces."""
    result = sanitize_text("hello\x01world\x0etest")
    assert result == "hello world test"


def test_sanitize_text_preserves_newlines() -> None:
    """Newlines should be kept (they are valid in context text)."""
    assert sanitize_text("line1\nline2") == "line1\nline2"


def test_sanitize_term_name_valid() -> None:
    """Normal term names should pass through."""
    assert sanitize_term_name("Supervised Learning") == "Supervised Learning"
    assert sanitize_term_name("K-Nearest Neighbors") == "K-Nearest Neighbors"
    assert sanitize_term_name("A/B Testing") == "A/B Testing"


def test_sanitize_term_name_strips_html() -> None:
    """HTML angle brackets should be removed, preventing tag injection."""
    result = sanitize_term_name("<script>alert(1)</script>Compute")
    assert "<" not in result
    assert ">" not in result
    assert "Compute" in result


def test_sanitize_term_name_empty_raises() -> None:
    """Empty string after sanitization should raise ValueError."""
    with pytest.raises(ValueError, match="empty"):
        sanitize_term_name("   <>><<>  ")


def test_sanitize_context_allows_punctuation() -> None:
    """Common punctuation should be preserved in context."""
    text = "This is useful for NLP tasks, e.g. sentiment analysis."
    assert sanitize_context(text) == text


def test_build_issue_body_contains_json() -> None:
    """Issue body should contain a valid JSON code block."""
    body = build_issue_body("Compute", "ml_fundamentals", "beginner", "Test context")
    assert "```json" in body
    assert "```" in body
    # Extract and parse the JSON block
    start = body.index("```json\n") + len("```json\n")
    end = body.index("\n```", start)
    parsed = json.loads(body[start:end])
    assert parsed["term_name"] == "Compute"
    assert parsed["category"] == "ml_fundamentals"


def test_build_issue_body_escapes_quotes() -> None:
    """Term names with quotes should be properly escaped in JSON."""
    body = build_issue_body('Bayes\' Theorem', "statistics", "intermediate", "")
    start = body.index("```json\n") + len("```json\n")
    end = body.index("\n```", start)
    parsed = json.loads(body[start:end])
    assert parsed["term_name"] == "Bayes' Theorem"
