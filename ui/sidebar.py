"""Sidebar UI: category dropdown, difficulty filter, search input, and suggestions."""

import streamlit as st

from core.constants import (
    APP_TITLE,
    CATEGORY_DISPLAY_NAMES,
    SEARCH_PLACEHOLDER,
)
from core.loader import compute_term_counts
from core.models import Term
from core.search import get_available_letters, search_suggestions


def _init_session_state() -> None:
    """Initialize session state keys with defaults if not already set."""
    if "selected_term" not in st.session_state:
        st.session_state.selected_term = None
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = None
    if "selected_difficulty" not in st.session_state:
        st.session_state.selected_difficulty = None
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "term_history" not in st.session_state:
        st.session_state.term_history = []
    if "selected_letter" not in st.session_state:
        st.session_state.selected_letter = None


def _filter_by_difficulty(terms: list[Term]) -> list[Term]:
    """Filter a term list by the currently selected difficulty.

    Args:
        terms: List of terms to filter.

    Returns:
        Filtered list, or the original list if no difficulty is selected.
    """
    difficulty = st.session_state.selected_difficulty
    if not difficulty:
        return terms
    return [t for t in terms if t.difficulty == difficulty]


def render_sidebar(
    terms_by_slug: dict[str, Term],
    terms_by_category: dict[str, list[Term]],
) -> None:
    """Render the sidebar with all filters, browse, and search.

    Args:
        terms_by_slug: Complete slug-to-Term mapping.
        terms_by_category: Category-key-to-term-list mapping.
    """
    _init_session_state()

    st.sidebar.title(APP_TITLE)

    counts_by_cat, counts_by_diff = compute_term_counts(
        terms_by_slug, terms_by_category
    )

    _render_category_dropdown(terms_by_category, counts_by_cat)
    _render_difficulty_filter(counts_by_diff)
    _render_term_browser(terms_by_category)
    _render_search_input(terms_by_slug)
    _render_clear_button()


def _render_category_dropdown(
    terms_by_category: dict[str, list[Term]],
    counts: dict[str, int],
) -> None:
    """Render the category filter selectbox with term counts."""
    options: list[str | None] = [None] + sorted(terms_by_category.keys())

    def fmt(key: str | None) -> str:
        if key is None:
            total = sum(counts.values())
            return f"All Categories ({total})"
        name = CATEGORY_DISPLAY_NAMES.get(key, key)
        return f"{name} ({counts.get(key, 0)})"

    selected = st.sidebar.selectbox(
        "Category", options, format_func=fmt
    )
    st.session_state.selected_category = selected


def _render_difficulty_filter(counts: dict[str, int]) -> None:
    """Render difficulty level radio buttons with term counts."""
    options: list[str | None] = [None, "beginner", "intermediate", "advanced"]

    def fmt(key: str | None) -> str:
        if key is None:
            total = sum(counts.values())
            return f"All Levels ({total})"
        return f"{key.capitalize()} ({counts.get(key, 0)})"

    selected = st.sidebar.radio(
        "Difficulty", options, format_func=fmt, horizontal=True
    )
    st.session_state.selected_difficulty = selected


def _render_term_browser(
    terms_by_category: dict[str, list[Term]],
) -> None:
    """Render a two-step term browser: letter selector + filtered dropdown."""
    category_key = st.session_state.selected_category
    if category_key:
        browsable = terms_by_category.get(category_key, [])
    else:
        browsable = [
            t for terms in terms_by_category.values() for t in terms
        ]
    browsable = _filter_by_difficulty(browsable)

    letters = get_available_letters(browsable)
    if not letters:
        return

    _render_letter_selector(letters)
    _render_filtered_dropdown(browsable)


def _render_letter_selector(letters: list[str]) -> None:
    """Render a horizontal radio for letter selection.

    Args:
        letters: Available first letters.
    """
    options: list[str | None] = [None] + letters

    def fmt(val: str | None) -> str:
        return "All" if val is None else val

    selected = st.sidebar.radio(
        "Browse A\u2013Z",
        options,
        format_func=fmt,
        horizontal=True,
    )
    st.session_state.selected_letter = selected


def _render_filtered_dropdown(browsable: list[Term]) -> None:
    """Render the term selectbox filtered by selected letter.

    Args:
        browsable: Pre-filtered list of terms.
    """
    letter = st.session_state.selected_letter
    if letter:
        filtered = [t for t in browsable if t.term[0].upper() == letter]
    else:
        filtered = browsable
    filtered = sorted(filtered, key=lambda t: t.term)

    placeholder = "Browse terms\u2026"
    options = [placeholder] + [t.term for t in filtered]

    # Build a lookup so the on_change callback can resolve the slug
    name_to_slug = {t.term: t.slug for t in filtered}

    def _on_browse_select() -> None:
        """Callback: set selected_term and reset dropdown to placeholder."""
        val = st.session_state.get("_browse_selectbox", placeholder)
        if val != placeholder and val in name_to_slug:
            st.session_state.selected_term = name_to_slug[val]
        # Reset dropdown so it doesn't re-trigger on next rerun
        st.session_state._browse_selectbox = placeholder

    st.sidebar.selectbox(
        "Browse",
        options,
        key="_browse_selectbox",
        label_visibility="collapsed",
        on_change=_on_browse_select,
    )


def _render_search_input(terms_by_slug: dict[str, Term]) -> None:
    """Render the search text input and fuzzy suggestions."""
    query = st.sidebar.text_input(SEARCH_PLACEHOLDER, value="")
    st.session_state.search_query = query

    if not query.strip():
        return

    suggestions = search_suggestions(
        query,
        terms_by_slug,
        limit=3,
        category_filter=st.session_state.selected_category,
    )
    for suggestion in suggestions:
        if st.sidebar.button(
            suggestion.term, key=f"suggest_{suggestion.slug}"
        ):
            st.session_state.selected_term = suggestion.slug
            st.rerun()


def _render_clear_button() -> None:
    """Render a button that resets all filters and selection."""
    if st.sidebar.button("Reset Filters"):
        st.session_state.selected_term = None
        st.session_state.selected_category = None
        st.session_state.selected_difficulty = None
        st.session_state.search_query = ""
        st.session_state.term_history = []
        st.session_state.selected_letter = None
        st.rerun()
