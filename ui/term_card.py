"""Renders a single term's full detail view."""

import html

import streamlit as st

from core.constants import (
    ANALOGY_PREFIX,
    CATEGORY_DISPLAY_NAMES,
    DIFFICULTY_COLORS,
    SENTENCE_PREFIX,
)
from core.models import Term
from core.navigation import pop_term_history

_CARD_STYLES: str = """
<style>
.difficulty-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.85em;
    color: #fff;
}
.difficulty-badge-beginner { background-color: green; }
.difficulty-badge-intermediate { background-color: orange; }
.difficulty-badge-advanced { background-color: red; }
.tag-pill {
    display: inline-block;
    background: rgba(128,128,128,0.2);
    color: inherit;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.8em;
    margin-right: 4px;
}
</style>
"""


def _inject_card_styles() -> None:
    """Emit the shared CSS style block for term card elements."""
    st.markdown(_CARD_STYLES, unsafe_allow_html=True)


def _render_difficulty_badge(difficulty: str) -> None:
    """Display a color-coded difficulty badge.

    Args:
        difficulty: One of 'beginner', 'intermediate', 'advanced'.
    """
    safe_diff = html.escape(difficulty)
    st.markdown(
        f'<span class="difficulty-badge difficulty-badge-{safe_diff}">'
        f"{safe_diff}</span>",
        unsafe_allow_html=True,
    )


def _render_tags(tags: list[str]) -> None:
    """Display tags as pill-style badges.

    Args:
        tags: List of tag strings.
    """
    pills = " ".join(
        f'<span class="tag-pill">{html.escape(tag)}</span>' for tag in tags
    )
    st.markdown(pills, unsafe_allow_html=True)


def _render_nav_buttons(terms_by_slug: dict[str, Term]) -> None:
    """Show Home and Back buttons for navigation.

    Args:
        terms_by_slug: Slug-to-Term mapping for display name lookup.
    """
    history = st.session_state.get("term_history", [])
    cols = st.columns([1, 2, 9]) if history else st.columns([1, 11])

    with cols[0]:
        if st.button("Home"):
            st.session_state.selected_term = None
            st.session_state.term_history = []
            st.rerun()

    if history:
        prev_slug = history[-1]
        prev_term = terms_by_slug.get(prev_slug)
        label = (
            f"\u2190 Back to {prev_term.term}" if prev_term else "\u2190 Back"
        )
        with cols[1]:
            if st.button(label):
                popped, remaining = pop_term_history(history)
                st.session_state.term_history = remaining
                st.session_state.selected_term = popped
                st.rerun()


def render_term_card(
    term: Term,
    terms_by_slug: dict[str, Term] | None = None,
) -> None:
    """Render the full detail view for a single term.

    Args:
        term: The Term object to display.
        terms_by_slug: Optional slug-to-Term mapping for back navigation.
    """
    _inject_card_styles()

    if terms_by_slug:
        _render_nav_buttons(terms_by_slug)

    st.title(term.term)
    _render_difficulty_badge(term.difficulty)

    category_name = CATEGORY_DISPLAY_NAMES.get(term.category, term.category)
    st.caption(category_name)

    st.write(term.definition)
    st.info(f"{ANALOGY_PREFIX}\n\n{term.analogy}")
    st.success(f"{SENTENCE_PREFIX}\n\n{term.use_in_a_sentence}")

    st.markdown("**Business Context**")
    st.write(term.business_context)

    _render_tags(term.tags)
