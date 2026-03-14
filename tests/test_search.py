"""Tests for fuzzy search logic."""

from core.models import Term
from core.search import search_best_match, search_suggestions


def test_exact_match_returns_correct_term(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """Searching the exact term name should return it."""
    result = search_best_match("Alpha Term", sample_terms_by_slug)
    assert result is not None
    assert result.slug == "alpha-term"


def test_partial_match_returns_correct_term(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """A misspelled or partial query should still match."""
    result = search_best_match("Alph Trm", sample_terms_by_slug)
    assert result is not None
    assert result.slug == "alpha-term"


def test_gibberish_returns_none(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """A completely unrelated query should return None."""
    result = search_best_match("xyzzy123qqq", sample_terms_by_slug)
    assert result is None


def test_suggestions_returns_multiple(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """search_suggestions should return a list of matching terms."""
    results = search_suggestions("term", sample_terms_by_slug, limit=5)
    assert len(results) >= 1
    assert all(isinstance(t, Term) for t in results)


def test_category_filter_restricts_results(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """Filtering by a non-matching category should return None."""
    result = search_best_match(
        "Alpha Term", sample_terms_by_slug, category_filter="nonexistent_category"
    )
    assert result is None


def test_tag_search_finds_term(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """Searching for a tag value should surface the tagged term."""
    result = search_best_match("validation", sample_terms_by_slug)
    assert result is not None
    assert result.slug == "beta-term"
