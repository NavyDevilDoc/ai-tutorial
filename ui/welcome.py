"""Welcome page with search hero and quick-start terms."""

import streamlit as st

from core.constants import (
    QUICK_START_SLUGS,
    WELCOME_HEADING,
    WELCOME_SUBTEXT,
)
from core.models import Term
from core.search import search_best_match


def _render_hero_search(terms_by_slug: dict[str, Term]) -> None:
    """Render the main search box on the landing page.

    Args:
        terms_by_slug: Complete slug-to-Term mapping for search.
    """
    query = st.text_input(
        "Search",
        placeholder="e.g. transformer, overfitting, RAG\u2026",
        label_visibility="collapsed",
    )
    if query.strip():
        match = search_best_match(query, terms_by_slug)
        if match:
            st.session_state.selected_term = match.slug
            st.rerun()
        else:
            st.caption("No match found. Try a different term.")


def _render_quick_starts(terms_by_slug: dict[str, Term]) -> None:
    """Render a row of quick-start term buttons.

    Args:
        terms_by_slug: Complete slug-to-Term mapping.
    """
    st.markdown("**Popular starting points:**")
    valid = [
        terms_by_slug[s] for s in QUICK_START_SLUGS if s in terms_by_slug
    ]
    cols = st.columns(min(len(valid), 3))
    for i, term in enumerate(valid):
        with cols[i % 3]:
            if st.button(term.term, key=f"quick_{term.slug}"):
                st.session_state.selected_term = term.slug
                st.rerun()


def render_welcome_page(
    terms_by_slug: dict[str, Term],
    terms_by_category: dict[str, list[Term]],
) -> None:
    """Render the landing page with search hero and quick-start terms.

    Args:
        terms_by_slug: Complete slug-to-Term mapping.
        terms_by_category: Category-key-to-term-list mapping.
    """
    st.markdown("")
    st.header(WELCOME_HEADING)
    st.write(WELCOME_SUBTEXT)
    st.markdown("")

    _render_hero_search(terms_by_slug)

    st.markdown("---")
    _render_quick_starts(terms_by_slug)

    total = len(terms_by_slug)
    cats = len(terms_by_category)
    st.caption(
        f"{total} terms across {cats} categories."
        " Use the sidebar to browse by category, difficulty, or letter."
    )
