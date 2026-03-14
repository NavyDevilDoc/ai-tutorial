"""Tests for Pydantic Term and Category models."""

import pytest
from pydantic import ValidationError

from core.models import Category, Term, validate_related_terms

VALID_TERM_DATA: dict = {
    "term": "Test Term",
    "slug": "test-term",
    "category": "test_category",
    "difficulty": "beginner",
    "definition": "A term used for testing.",
    "analogy": "Like a crash test dummy for software.",
    "use_in_a_sentence": "We created a test term to verify the model.",
    "business_context": "Essential for quality assurance.",
    "related_terms": [],
    "tags": ["test"],
}


def test_valid_term_creates_successfully() -> None:
    """A complete, valid term dict should construct without error."""
    term = Term(**VALID_TERM_DATA)
    assert term.slug == "test-term"
    assert term.difficulty == "beginner"


def test_missing_required_field_raises_validation_error() -> None:
    """Omitting a required field should raise ValidationError."""
    for field in ["term", "slug", "definition", "analogy", "use_in_a_sentence"]:
        data = {**VALID_TERM_DATA}
        del data[field]
        with pytest.raises(ValidationError):
            Term(**data)


def test_invalid_difficulty_raises_validation_error() -> None:
    """A difficulty value outside the allowed set should fail."""
    data = {**VALID_TERM_DATA, "difficulty": "expert"}
    with pytest.raises(ValidationError):
        Term(**data)


def test_invalid_slug_format_raises_validation_error() -> None:
    """Slugs with uppercase or spaces should fail validation."""
    for bad_slug in ["Test-Term", "test term", "TEST", "test_term"]:
        data = {**VALID_TERM_DATA, "slug": bad_slug}
        with pytest.raises(ValidationError):
            Term(**data)


def test_valid_slug_formats() -> None:
    """Various valid slug formats should pass."""
    for good_slug in ["test", "test-term", "a-b-c", "ml101"]:
        data = {**VALID_TERM_DATA, "slug": good_slug}
        term = Term(**data)
        assert term.slug == good_slug


def test_validate_related_terms_passes_with_valid_slugs() -> None:
    """Related terms validation should pass when all slugs exist."""
    data = {**VALID_TERM_DATA, "related_terms": ["other-term"]}
    term = Term(**data)
    validate_related_terms(term, {"test-term", "other-term"})


def test_validate_related_terms_raises_on_missing_slug() -> None:
    """Related terms validation should fail on dangling references."""
    data = {**VALID_TERM_DATA, "related_terms": ["nonexistent"]}
    term = Term(**data)
    with pytest.raises(ValueError, match="nonexistent"):
        validate_related_terms(term, {"test-term"})


def test_category_model() -> None:
    """Category model should accept a list of Terms."""
    term = Term(**VALID_TERM_DATA)
    cat = Category(name="Test", file_key="test_category", terms=[term])
    assert len(cat.terms) == 1
