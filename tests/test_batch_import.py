"""Tests for batch import functionality."""

import json
from pathlib import Path

import pytest

import tools.add_term as add_term_module
from tools.add_term import _validate_batch, _load_batch_terms, validate_term_against


def _make_term(
    name: str,
    slug: str,
    category: str = "test",
    difficulty: str = "beginner",
    related: list[str] | None = None,
) -> dict:
    """Helper to build a minimal valid term dict."""
    return {
        "term": name,
        "slug": slug,
        "category": category,
        "difficulty": difficulty,
        "definition": f"Definition of {name}.",
        "analogy": f"Like something related to {name}.",
        "use_in_a_sentence": f"We used {name} in our project.",
        "business_context": f"{name} is important for business.",
        "related_terms": related or [],
        "tags": ["test"],
    }


def test_batch_validate_mutual_references() -> None:
    """Terms in a batch that reference each other should both pass."""
    terms = [
        _make_term("Alpha", "alpha", related=["beta"]),
        _make_term("Beta", "beta", related=["alpha"]),
    ]
    errors = _validate_batch(terms, existing_slugs=set())
    assert errors == []


def test_batch_validate_duplicate_within_batch() -> None:
    """Two terms with the same slug in one batch should error."""
    terms = [
        _make_term("Alpha One", "alpha"),
        _make_term("Alpha Two", "alpha"),
    ]
    errors = _validate_batch(terms, existing_slugs=set())
    assert len(errors) > 0
    assert any("Duplicate" in msg for _, msg in errors)


def test_batch_validate_duplicate_with_existing() -> None:
    """A new term slug that matches an existing slug should error."""
    terms = [_make_term("Model", "model")]
    errors = _validate_batch(terms, existing_slugs={"model", "feature"})
    assert len(errors) == 1
    assert "already exists" in errors[0][1]


def test_batch_validate_schema_error() -> None:
    """A term with invalid schema should report the error."""
    terms = [{"slug": "bad", "category": "test"}]  # missing required fields
    errors = _validate_batch(terms, existing_slugs=set())
    assert len(errors) == 1
    assert "Schema error" in errors[0][1]


def test_batch_atomic_no_write_on_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If any term in a batch fails, no terms should be written."""
    monkeypatch.setattr(add_term_module, "DATA_DIR", tmp_path)

    # Create an existing category file
    (tmp_path / "test.json").write_text("[]", encoding="utf-8")

    # Batch with one good term and one bad term (invalid difficulty)
    terms_file = tmp_path / "batch.json"
    terms_file.write_text(json.dumps([
        _make_term("Good Term", "good-term"),
        {
            "term": "Bad", "slug": "bad", "category": "test",
            "difficulty": "INVALID", "definition": "x", "analogy": "x",
            "use_in_a_sentence": "x", "business_context": "x",
            "related_terms": [], "tags": [],
        },
    ]), encoding="utf-8")

    with pytest.raises(SystemExit):
        add_term_module.batch_import(terms_file)

    # Verify nothing was written
    data = json.loads((tmp_path / "test.json").read_text(encoding="utf-8"))
    assert len(data) == 0


def test_batch_cross_references_pass() -> None:
    """The core use case: A references B, B references A, both in batch."""
    terms = [
        _make_term("Few-Shot", "few-shot", related=["zero-shot"]),
        _make_term("Zero-Shot", "zero-shot", related=["few-shot"]),
    ]
    errors = _validate_batch(terms, existing_slugs=set())
    assert errors == []


def test_load_batch_from_directory(tmp_path: Path) -> None:
    """Loading from a directory should collect all .json files."""
    (tmp_path / "a.json").write_text(
        json.dumps(_make_term("Alpha", "alpha")), encoding="utf-8"
    )
    (tmp_path / "b.json").write_text(
        json.dumps(_make_term("Beta", "beta")), encoding="utf-8"
    )
    terms = _load_batch_terms(tmp_path)
    assert len(terms) == 2
    slugs = {t["slug"] for t in terms}
    assert slugs == {"alpha", "beta"}


def test_validate_term_against_accepts_new_slug() -> None:
    """validate_term_against should pass for a new unique slug."""
    term = _make_term("New Thing", "new-thing")
    ok, err = validate_term_against(term, {"existing-term"})
    assert ok is True
    assert err == ""


def test_validate_term_against_rejects_existing_slug() -> None:
    """validate_term_against should fail for a duplicate slug."""
    term = _make_term("Existing", "existing-term")
    ok, err = validate_term_against(term, {"existing-term"})
    assert ok is False
    assert "already exists" in err
