"""Tests for GitHub Action term processing script."""

import sys
from pathlib import Path

import pytest

# Add .github/scripts to path so we can import the module
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".github" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import process_approved_term as pat
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


FULL_FORM_ISSUE_BODY: str = """## Suggested Term

| Field | Value |
|---|---|
| Term | Autoencoder |
| Category | neural_networks |
| Difficulty | advanced |

### Definition

A neural network that learns to compress data.

### Analogy

Like summarizing a book.

### Structured Data

```json
{
  "term_name": "Autoencoder",
  "category": "neural_networks",
  "difficulty": "advanced",
  "context": "heard it in standup",
  "definition": "A neural network that learns to compress data.",
  "analogy": "Like summarizing a book.",
  "use_in_a_sentence": "We trained an autoencoder on transactions.",
  "business_context": "Used in fraud detection."
}
```"""


def test_extract_valid_body() -> None:
    """Valid minimum issue body should parse correctly."""
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


# ---------------------------------------------------------------------------
# User-provided prose fields (Phase 6 / Option A)
# ---------------------------------------------------------------------------


def test_extract_includes_user_prose_fields() -> None:
    """User-provided prose fields should be extracted when present."""
    data = extract_term_data_from_issue(FULL_FORM_ISSUE_BODY)
    assert data["definition"] == "A neural network that learns to compress data."
    assert data["analogy"] == "Like summarizing a book."
    assert data["use_in_a_sentence"] == "We trained an autoencoder on transactions."
    assert data["business_context"] == "Used in fraud detection."


def test_extract_omits_prose_fields_when_absent() -> None:
    """Minimum payload should not surface empty prose keys."""
    data = extract_term_data_from_issue(VALID_ISSUE_BODY)
    for field in ("definition", "analogy", "use_in_a_sentence", "business_context"):
        assert field not in data


def test_extract_strips_html_from_prose_fields() -> None:
    """Prose fields are sanitized (control chars removed) like other text."""
    body = (
        "```json\n"
        '{"term_name": "Test", "category": "ml_fundamentals", "difficulty": "beginner",'
        ' "definition": "A term\\u0001with control chars", "analogy": "  padded  "}\n'
        "```"
    )
    data = extract_term_data_from_issue(body)
    assert "\x01" not in data["definition"]
    assert data["analogy"] == "padded"


def test_generate_and_validate_overlays_user_prose(monkeypatch: pytest.MonkeyPatch) -> None:
    """User-provided prose should overwrite the LLM output for those fields."""
    llm_output = {
        "term": "Autoencoder",
        "slug": "autoencoder-x",
        "category": "neural_networks",
        "difficulty": "advanced",
        "definition": "LLM-written definition",
        "analogy": "LLM analogy",
        "use_in_a_sentence": "LLM sentence",
        "business_context": "LLM business context",
        "related_terms": [],
        "tags": ["ae"],
    }
    monkeypatch.setattr(
        "tools.add_term.generate_term_with_llm", lambda *a, **kw: dict(llm_output)
    )
    monkeypatch.setattr(
        "tools.add_term.make_slug", lambda name: "autoencoder-x"
    )
    monkeypatch.setattr(
        "core.data_loading.load_all_terms_impl", lambda: ({}, {})
    )

    result = pat.generate_and_validate_term(
        "Autoencoder",
        "neural_networks",
        "advanced",
        user_fields={
            "definition": "User-written definition",
            "analogy": "User analogy",
        },
    )

    assert result["definition"] == "User-written definition"
    assert result["analogy"] == "User analogy"
    # Fields the user didn't provide stay as LLM output
    assert result["use_in_a_sentence"] == "LLM sentence"
    assert result["business_context"] == "LLM business context"


def test_generate_and_validate_uses_llm_when_no_user_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """When user provides no prose, LLM output flows through unchanged."""
    llm_output = {
        "term": "Thing",
        "slug": "thing-x",
        "category": "ml_fundamentals",
        "difficulty": "beginner",
        "definition": "LLM definition",
        "analogy": "LLM analogy",
        "use_in_a_sentence": "LLM sentence",
        "business_context": "LLM context",
        "related_terms": [],
        "tags": ["t"],
    }
    monkeypatch.setattr(
        "tools.add_term.generate_term_with_llm", lambda *a, **kw: dict(llm_output)
    )
    monkeypatch.setattr(
        "tools.add_term.make_slug", lambda name: "thing-x"
    )
    monkeypatch.setattr(
        "core.data_loading.load_all_terms_impl", lambda: ({}, {})
    )

    result = pat.generate_and_validate_term(
        "Thing", "ml_fundamentals", "beginner", user_fields=None
    )

    assert result["definition"] == "LLM definition"
    assert result["analogy"] == "LLM analogy"
