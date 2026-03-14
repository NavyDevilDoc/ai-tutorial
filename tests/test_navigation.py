"""Tests for term navigation history logic."""

from core.navigation import pop_term_history, push_term_history


def test_push_increases_stack_length() -> None:
    """Pushing a slug should add it to the end of history."""
    history = push_term_history([], "term-a")
    assert history == ["term-a"]
    history = push_term_history(history, "term-b")
    assert history == ["term-a", "term-b"]


def test_pop_returns_most_recent() -> None:
    """Popping should return the last slug and shorten the stack."""
    history = ["term-a", "term-b", "term-c"]
    slug, remaining = pop_term_history(history)
    assert slug == "term-c"
    assert remaining == ["term-a", "term-b"]


def test_pop_from_empty_returns_none() -> None:
    """Popping an empty stack should return None."""
    slug, remaining = pop_term_history([])
    assert slug is None
    assert remaining == []


def test_push_respects_max_depth() -> None:
    """Pushing beyond max_depth should drop the oldest entry."""
    history = [f"term-{i}" for i in range(5)]
    history = push_term_history(history, "new-term", max_depth=5)
    assert len(history) == 5
    assert history[0] == "term-1"
    assert history[-1] == "new-term"


def test_push_empty_slug_is_noop() -> None:
    """Pushing an empty string should not change the history."""
    history = ["term-a"]
    result = push_term_history(history, "")
    assert result == ["term-a"]


def test_push_none_slug_is_noop() -> None:
    """Pushing None should not change the history."""
    history = ["term-a"]
    result = push_term_history(history, None)
    assert result == ["term-a"]
