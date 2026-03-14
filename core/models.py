"""Pydantic models for Term and Category data structures."""

import re
from typing import Literal

from pydantic import BaseModel, field_validator


class Term(BaseModel):
    """A single AI/ML glossary term with plain-language explanation."""

    term: str
    slug: str
    category: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    definition: str
    analogy: str
    use_in_a_sentence: str
    business_context: str
    related_terms: list[str]
    tags: list[str]

    @field_validator("slug")
    @classmethod
    def slug_must_be_lowercase_hyphenated(cls, v: str) -> str:
        """Validate that slug is lowercase and hyphen-separated."""
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", v):
            raise ValueError(
                f"Slug must be lowercase and hyphen-separated, got: '{v}'"
            )
        return v


class Category(BaseModel):
    """A grouping of related terms under a display name."""

    name: str
    file_key: str
    terms: list[Term]


def validate_related_terms(term: Term, all_slugs: set[str]) -> None:
    """Check that all related_terms slugs exist in the full term index.

    Args:
        term: The term whose related_terms to validate.
        all_slugs: Set of all known slugs across every category.

    Raises:
        ValueError: If any related_terms slug is not in all_slugs.
    """
    for slug in term.related_terms:
        if slug not in all_slugs:
            raise ValueError(
                f"Term '{term.slug}' references unknown related term '{slug}'"
            )
