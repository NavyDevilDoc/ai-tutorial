"""Tests for alphabet browsing and grouping logic."""

from core.models import Term
from core.search import get_available_letters, group_terms_by_letter


def test_get_available_letters(sample_terms_list: list[Term]) -> None:
    """Should return sorted unique first letters."""
    letters = get_available_letters(sample_terms_list)
    assert letters == ["A", "B", "D", "G"]


def test_group_terms_by_letter(sample_terms_list: list[Term]) -> None:
    """Should group terms correctly by first letter."""
    groups = group_terms_by_letter(sample_terms_list)
    assert "A" in groups
    assert len(groups["A"]) == 1
    assert groups["A"][0].slug == "alpha-term"
    assert "B" in groups
    assert len(groups["B"]) == 1
    assert "D" in groups
    assert "G" in groups


def test_group_terms_sorted_within_letter(
    sample_terms_list: list[Term],
) -> None:
    """Terms within each letter group should be alphabetically sorted."""
    groups = group_terms_by_letter(sample_terms_list)
    for terms in groups.values():
        names = [t.term for t in terms]
        assert names == sorted(names)


def test_empty_list_returns_empty() -> None:
    """Empty input should produce empty results."""
    assert get_available_letters([]) == []
    assert group_terms_by_letter([]) == {}
