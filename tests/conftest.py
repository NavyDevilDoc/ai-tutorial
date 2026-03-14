"""Shared pytest fixtures for the AI Literacy Tutor test suite."""

import json
from collections import defaultdict
from pathlib import Path

import pytest

from core.models import Term

_FIXTURE_PATH: Path = Path(__file__).parent / "fixtures" / "valid_terms.json"


@pytest.fixture
def sample_terms_list() -> list[Term]:
    """Load all terms from the fixture file as a list."""
    raw = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    return [Term(**entry) for entry in raw]


@pytest.fixture
def sample_terms_by_slug(sample_terms_list: list[Term]) -> dict[str, Term]:
    """Build a slug-to-Term mapping from fixture data."""
    return {t.slug: t for t in sample_terms_list}


@pytest.fixture
def sample_terms_by_category(
    sample_terms_list: list[Term],
) -> dict[str, list[Term]]:
    """Build a category-to-term-list mapping from fixture data."""
    by_cat: dict[str, list[Term]] = defaultdict(list)
    for t in sample_terms_list:
        by_cat[t.category].append(t)
    return dict(by_cat)
