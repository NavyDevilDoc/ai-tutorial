"""Loads and validates all JSON term data at startup."""

import json
from pathlib import Path

import streamlit as st

from core.constants import CATEGORY_DISPLAY_NAMES
from core.models import Term, validate_related_terms

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"


def _load_all_terms_impl() -> tuple[dict[str, Term], dict[str, list[Term]]]:
    """Load all term JSON files, validate, and build lookup structures.

    Returns:
        A tuple of (terms_by_slug, terms_by_category).

    Raises:
        ValueError: If any term fails validation or has a dangling related_terms reference.
    """
    terms_by_slug: dict[str, Term] = {}
    terms_by_category: dict[str, list[Term]] = {}

    for file_path in sorted(DATA_DIR.glob("*.json")):
        if file_path.name.startswith("_"):
            continue

        raw_entries = json.loads(file_path.read_text(encoding="utf-8"))
        category_key = file_path.stem
        category_terms: list[Term] = []

        for entry in raw_entries:
            try:
                term = Term(**entry)
            except Exception as exc:
                slug = entry.get("slug", "unknown")
                raise ValueError(f"Invalid term '{slug}': {exc}") from exc

            if term.slug in terms_by_slug:
                raise ValueError(f"Duplicate slug: '{term.slug}'")

            terms_by_slug[term.slug] = term
            category_terms.append(term)

        terms_by_category[category_key] = category_terms

    _validate_all_related_terms(terms_by_slug)
    return terms_by_slug, terms_by_category


def _validate_all_related_terms(terms_by_slug: dict[str, Term]) -> None:
    """Check that every related_terms reference points to an existing slug.

    Args:
        terms_by_slug: Complete mapping of slug to Term.

    Raises:
        ValueError: If any related_terms slug is missing from the index.
    """
    all_slugs = set(terms_by_slug.keys())
    for term in terms_by_slug.values():
        validate_related_terms(term, all_slugs)


@st.cache_resource
def load_all_terms() -> tuple[dict[str, Term], dict[str, list[Term]]]:
    """Cached wrapper that loads all terms once per Streamlit session.

    Returns:
        A tuple of (terms_by_slug, terms_by_category).
    """
    return _load_all_terms_impl()


def compute_term_counts(
    terms_by_slug: dict[str, Term],
    terms_by_category: dict[str, list[Term]],
) -> tuple[dict[str, int], dict[str, int]]:
    """Compute term counts grouped by category and by difficulty.

    Args:
        terms_by_slug: Complete slug-to-Term mapping.
        terms_by_category: Category-key-to-term-list mapping.

    Returns:
        A tuple of (counts_by_category, counts_by_difficulty).
    """
    counts_by_category = {k: len(v) for k, v in terms_by_category.items()}
    counts_by_difficulty: dict[str, int] = {}
    for term in terms_by_slug.values():
        counts_by_difficulty[term.difficulty] = (
            counts_by_difficulty.get(term.difficulty, 0) + 1
        )
    return counts_by_category, counts_by_difficulty


def compute_category_difficulty_counts(
    terms: list[Term],
) -> dict[str, int]:
    """Count terms per difficulty level within a single category.

    Args:
        terms: List of terms in one category.

    Returns:
        Dict mapping difficulty level to count.
    """
    counts: dict[str, int] = {}
    for term in terms:
        counts[term.difficulty] = counts.get(term.difficulty, 0) + 1
    return counts


def get_category_display_name(category_key: str) -> str:
    """Return the human-readable display name for a category key.

    Args:
        category_key: The file stem key (e.g. 'ml_fundamentals').

    Returns:
        Display name string.
    """
    return CATEGORY_DISPLAY_NAMES.get(category_key, category_key)
