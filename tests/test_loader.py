"""Tests for the data loader module."""

import json
import tempfile
from pathlib import Path

import pytest

from core.loader import (
    _load_all_terms_impl,
    compute_category_difficulty_counts,
    compute_term_counts,
)
from core.models import Term
import core.loader as loader_module


@pytest.fixture
def valid_data_dir(tmp_path: Path) -> Path:
    """Create a temp directory with valid term JSON files."""
    terms = [
        {
            "term": "Alpha",
            "slug": "alpha",
            "category": "test",
            "difficulty": "beginner",
            "definition": "First term.",
            "analogy": "Like the letter A.",
            "use_in_a_sentence": "Alpha was loaded first.",
            "business_context": "Testing.",
            "related_terms": ["beta"],
            "tags": ["test"],
        },
        {
            "term": "Beta",
            "slug": "beta",
            "category": "test",
            "difficulty": "intermediate",
            "definition": "Second term.",
            "analogy": "Like the letter B.",
            "use_in_a_sentence": "Beta was loaded second.",
            "business_context": "Testing.",
            "related_terms": ["alpha"],
            "tags": ["test"],
        },
    ]
    (tmp_path / "test.json").write_text(json.dumps(terms), encoding="utf-8")
    return tmp_path


@pytest.fixture
def invalid_data_dir(tmp_path: Path) -> Path:
    """Create a temp directory with an invalid term (missing analogy)."""
    terms = [
        {
            "term": "Bad",
            "slug": "bad",
            "category": "test",
            "difficulty": "beginner",
            "definition": "Missing analogy.",
            "use_in_a_sentence": "Fail.",
            "business_context": "Fail.",
            "related_terms": [],
            "tags": [],
        }
    ]
    (tmp_path / "test.json").write_text(json.dumps(terms), encoding="utf-8")
    return tmp_path


@pytest.fixture
def dangling_ref_dir(tmp_path: Path) -> Path:
    """Create a temp directory with a dangling related_terms reference."""
    terms = [
        {
            "term": "Lonely",
            "slug": "lonely",
            "category": "test",
            "difficulty": "beginner",
            "definition": "Has a dangling ref.",
            "analogy": "Like a broken link.",
            "use_in_a_sentence": "Lonely references a missing term.",
            "business_context": "Testing.",
            "related_terms": ["nonexistent"],
            "tags": [],
        }
    ]
    (tmp_path / "test.json").write_text(json.dumps(terms), encoding="utf-8")
    return tmp_path


def test_valid_data_loads_successfully(
    valid_data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Valid JSON should load without error and build correct lookups."""
    monkeypatch.setattr(loader_module, "DATA_DIR", valid_data_dir)
    terms_by_slug, terms_by_category = _load_all_terms_impl()

    assert len(terms_by_slug) == 2
    assert "alpha" in terms_by_slug
    assert "beta" in terms_by_slug
    assert "test" in terms_by_category
    assert len(terms_by_category["test"]) == 2


def test_invalid_schema_raises_value_error(
    invalid_data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A term missing required fields should raise ValueError."""
    monkeypatch.setattr(loader_module, "DATA_DIR", invalid_data_dir)
    with pytest.raises(ValueError, match="Invalid term"):
        _load_all_terms_impl()


def test_dangling_related_terms_raises_value_error(
    dangling_ref_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A related_terms slug pointing to nothing should raise ValueError."""
    monkeypatch.setattr(loader_module, "DATA_DIR", dangling_ref_dir)
    with pytest.raises(ValueError, match="nonexistent"):
        _load_all_terms_impl()


def test_schema_file_is_skipped(
    valid_data_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Files starting with underscore should be skipped."""
    # Add a _schema.json that would fail if loaded
    (valid_data_dir / "_schema.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(loader_module, "DATA_DIR", valid_data_dir)
    terms_by_slug, _ = _load_all_terms_impl()
    assert len(terms_by_slug) == 2


def test_compute_term_counts_by_category(
    sample_terms_by_slug: dict[str, Term],
    sample_terms_by_category: dict[str, list[Term]],
) -> None:
    """compute_term_counts should return correct per-category counts."""
    counts_by_cat, _ = compute_term_counts(
        sample_terms_by_slug, sample_terms_by_category
    )
    assert counts_by_cat["test_category"] == 2
    assert counts_by_cat["other_category"] == 2


def test_compute_term_counts_by_difficulty(
    sample_terms_by_slug: dict[str, Term],
    sample_terms_by_category: dict[str, list[Term]],
) -> None:
    """compute_term_counts should return correct per-difficulty counts."""
    _, counts_by_diff = compute_term_counts(
        sample_terms_by_slug, sample_terms_by_category
    )
    assert counts_by_diff["beginner"] == 2
    assert counts_by_diff["intermediate"] == 1
    assert counts_by_diff["advanced"] == 1


def test_compute_category_difficulty_counts(
    sample_terms_by_category: dict[str, list[Term]],
) -> None:
    """Per-category difficulty counts should be correct."""
    counts = compute_category_difficulty_counts(
        sample_terms_by_category["test_category"]
    )
    assert counts["beginner"] == 1
    assert counts["intermediate"] == 1
    assert "advanced" not in counts

    counts_other = compute_category_difficulty_counts(
        sample_terms_by_category["other_category"]
    )
    assert counts_other["advanced"] == 1
    assert counts_other["beginner"] == 1


def test_all_slugs_are_url_safe() -> None:
    """Every slug in production data should be safe for URL query params."""
    terms_by_slug, _ = _load_all_terms_impl()
    for slug in terms_by_slug:
        assert slug == slug.lower(), f"Slug not lowercase: {slug}"
        assert " " not in slug, f"Slug contains space: {slug}"
        assert all(
            c.isalnum() or c == "-" for c in slug
        ), f"Slug has invalid chars: {slug}"
