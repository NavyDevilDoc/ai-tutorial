"""Input sanitization for user-submitted text.

Used by both the Streamlit suggestion form (Stage 2) and the
GitHub Action processing script (Stage 3). All user input passes
through these functions before reaching any API call or file write.
"""

import json
import re

MAX_TERM_NAME_LENGTH: int = 100
MAX_CONTEXT_LENGTH: int = 1000


def sanitize_text(raw: str, max_length: int = 500) -> str:
    """Strip, truncate, and clean a raw text string.

    Args:
        raw: User-provided text.
        max_length: Maximum allowed length after cleaning.

    Returns:
        Cleaned string.
    """
    text = raw.strip()
    text = text.replace("\x00", "")
    text = re.sub(r"[\x01-\x09\x0b-\x0c\x0e-\x1f]", " ", text)
    return text[:max_length]


def sanitize_term_name(raw: str) -> str:
    """Sanitize a term name to safe characters only.

    Allows: letters, digits, spaces, hyphens, parentheses, periods,
    forward slashes, and apostrophes (for terms like "Bayes' Theorem"
    or "A/B Testing").

    Args:
        raw: User-provided term name.

    Returns:
        Cleaned term name.

    Raises:
        ValueError: If the name is empty after sanitization.
    """
    text = sanitize_text(raw, max_length=MAX_TERM_NAME_LENGTH)
    text = re.sub(r"[^a-zA-Z0-9\s\-().'/]", "", text)
    text = text.strip()
    if not text:
        raise ValueError("Term name is empty after sanitization")
    return text


def sanitize_context(raw: str) -> str:
    """Sanitize optional context text with a broader character set.

    Args:
        raw: User-provided context description.

    Returns:
        Cleaned context string.
    """
    return sanitize_text(raw, max_length=MAX_CONTEXT_LENGTH)


def build_issue_body(
    term_name: str,
    category: str,
    difficulty: str,
    context: str,
) -> str:
    """Construct a structured GitHub Issue body with embedded JSON.

    User input is escaped via json.dumps() so it cannot break out of
    the JSON structure or inject markdown.

    Args:
        term_name: Sanitized term name.
        category: Category key.
        difficulty: Difficulty level.
        context: Optional context text.

    Returns:
        Formatted issue body string.
    """
    data = {
        "term_name": term_name,
        "category": category,
        "difficulty": difficulty,
        "context": context,
    }
    json_block = json.dumps(data, indent=2, ensure_ascii=False)

    return (
        f"## Suggested Term\n\n"
        f"| Field | Value |\n"
        f"|---|---|\n"
        f"| Term | {term_name} |\n"
        f"| Category | {category} |\n"
        f"| Difficulty | {difficulty} |\n\n"
        f"### Additional Context\n\n"
        f"{context if context else 'None provided.'}\n\n"
        f"### Structured Data\n\n"
        f"```json\n{json_block}\n```"
    )
