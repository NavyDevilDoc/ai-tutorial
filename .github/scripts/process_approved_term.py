#!/usr/bin/env python3
"""Process an approved term suggestion from a GitHub Issue.

This script runs inside a GitHub Action. It extracts term data from
the issue body, generates a full term entry via the Anthropic API,
validates it, and appends it to the correct category JSON file.

Environment variables:
  ISSUE_BODY         - The full body of the GitHub Issue
  ISSUE_NUMBER       - The issue number (for logging)
  ANTHROPIC_API_KEY  - Anthropic API key (GitHub Actions secret)
"""

import json
import os
import re
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.constants import CATEGORY_DISPLAY_NAMES
from core.sanitize import sanitize_term_name

VALID_CATEGORIES: list[str] = list(CATEGORY_DISPLAY_NAMES.keys())
VALID_DIFFICULTIES: list[str] = ["beginner", "intermediate", "advanced"]


def extract_term_data_from_issue(issue_body: str) -> dict:
    """Extract and validate term suggestion data from an issue body.

    Treats all data as untrusted — validates category and difficulty
    against known-good values, sanitizes the term name.

    Args:
        issue_body: Full markdown body of the GitHub Issue.

    Returns:
        Dict with keys: term_name, category, difficulty, context.

    Raises:
        ValueError: If the JSON block is missing, malformed, or
            contains invalid values.
    """
    match = re.search(
        r"```json\s*\n(.*?)\n```", issue_body, re.DOTALL
    )
    if not match:
        raise ValueError("No JSON code block found in issue body")

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in issue body: {exc}") from None

    term_name = data.get("term_name", "").strip()
    if not term_name:
        raise ValueError("Missing term_name in issue data")

    term_name = sanitize_term_name(term_name)

    category = data.get("category", "")
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category '{category}'. "
            f"Must be one of: {VALID_CATEGORIES}"
        )

    difficulty = data.get("difficulty", "beginner")
    if difficulty not in VALID_DIFFICULTIES:
        raise ValueError(
            f"Invalid difficulty '{difficulty}'. "
            f"Must be one of: {VALID_DIFFICULTIES}"
        )

    return {
        "term_name": term_name,
        "category": category,
        "difficulty": difficulty,
        "context": data.get("context", ""),
    }


def generate_and_validate_term(
    term_name: str,
    category: str,
    difficulty: str,
) -> dict:
    """Generate a full term entry and validate it.

    Args:
        term_name: Sanitized term name.
        category: Valid category key.
        difficulty: Valid difficulty level.

    Returns:
        Validated term dict ready to append to JSON.

    Raises:
        ValueError: If generation or validation fails.
    """
    from core.loader import _load_all_terms_impl
    from core.models import Term
    from tools.add_term import generate_term_with_llm, make_slug

    slug = make_slug(term_name)

    terms_by_slug, _ = _load_all_terms_impl()
    if slug in terms_by_slug:
        raise ValueError(f"Slug '{slug}' already exists in the glossary")

    term_data = generate_term_with_llm(term_name, slug, category, difficulty)
    if term_data is None:
        raise ValueError("LLM generation failed — check ANTHROPIC_API_KEY")

    try:
        Term(**term_data)
    except Exception as exc:
        raise ValueError(f"Generated term failed validation: {exc}") from None

    # Strip any related_terms that don't exist
    all_slugs = set(terms_by_slug.keys()) | {slug}
    term_data["related_terms"] = [
        s for s in term_data.get("related_terms", []) if s in all_slugs
    ]

    return term_data


def append_term_to_file(term_data: dict, category: str) -> Path:
    """Append a validated term to its category JSON file.

    Args:
        term_data: Validated term dict.
        category: Category file key.

    Returns:
        Path to the modified file.
    """
    from tools.add_term import append_to_category
    return append_to_category(term_data, category)


def main() -> None:
    """Run the term processing pipeline."""
    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "unknown")

    if not issue_body:
        print(f"Error: ISSUE_BODY is empty for issue #{issue_number}")
        sys.exit(1)

    try:
        data = extract_term_data_from_issue(issue_body)
        print(f"Extracted: {data['term_name']} ({data['category']})")

        term_data = generate_and_validate_term(
            data["term_name"], data["category"], data["difficulty"]
        )
        print(f"Generated and validated: {term_data['slug']}")

        path = append_term_to_file(term_data, data["category"])
        print(f"Appended to: {path}")

    except ValueError as exc:
        print(f"Error processing issue #{issue_number}: {exc}")
        sys.exit(1)
    except Exception:
        print(f"Unexpected error processing issue #{issue_number}")
        sys.exit(1)


if __name__ == "__main__":
    main()
