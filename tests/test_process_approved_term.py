"""Tests for GitHub Action term processing script."""

import sys
from pathlib import Path

import pytest

# Add .github/scripts to path so we can import the module
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".github" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from process_approved_term import extract_term_data_from_issue


VALID_ISSUE_BODY: str = """## Suggested Term

| Field | Value |
|---|---|
| Term | Compute |
| Category | ml_fundamentals |
| Difficulty | beginner |

### Additional Context

Processing power for AI.

### Structured Data

```json
{
  "term_name": "Compute",
  "category": "ml_fundamentals",
  "difficulty": "beginner",
  "context": "Processing power for AI."
}
```"""


def test_extract_valid_body() -> None:
    """Valid issue body should parse correctly."""
    data = extract_term_data_from_issue(VALID_ISSUE_BODY)
    assert data["term_name"] == "Compute"
    assert data["category"] == "ml_fundamentals"
    assert data["difficulty"] == "beginner"
    assert data["context"] == "Processing power for AI."


def test_extract_no_json_block_raises() -> None:
    """Missing JSON code block should raise ValueError."""
    with pytest.raises(ValueError, match="No JSON code block"):
        extract_term_data_from_issue("Just some text, no JSON here.")


def test_extract_invalid_json_raises() -> None:
    """Malformed JSON should raise ValueError."""
    body = "### Data\n\n```json\n{invalid json}\n```"
    with pytest.raises(ValueError, match="Invalid JSON"):
        extract_term_data_from_issue(body)


def test_extract_invalid_category_raises() -> None:
    """Unknown category should raise ValueError."""
    body = '```json\n{"term_name": "Test", "category": "fake_category", "difficulty": "beginner"}\n```'
    with pytest.raises(ValueError, match="Invalid category"):
        extract_term_data_from_issue(body)


def test_extract_sanitizes_term_name() -> None:
    """HTML injection in term name should be stripped."""
    body = '```json\n{"term_name": "<script>alert(1)</script>Compute", "category": "ml_fundamentals", "difficulty": "beginner"}\n```'
    data = extract_term_data_from_issue(body)
    assert "<" not in data["term_name"]
    assert ">" not in data["term_name"]
    assert "Compute" in data["term_name"]


def test_extract_invalid_difficulty_raises() -> None:
    """Unknown difficulty should raise ValueError."""
    body = '```json\n{"term_name": "Test", "category": "ml_fundamentals", "difficulty": "expert"}\n```'
    with pytest.raises(ValueError, match="Invalid difficulty"):
        extract_term_data_from_issue(body)
