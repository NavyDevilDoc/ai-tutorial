"""Related terms sidebar panel."""

import streamlit as st

from core.models import Term
from core.navigation import push_term_history


def render_related_panel(
    term: Term,
    terms_by_slug: dict[str, Term],
) -> None:
    """Display up to 4 related terms in the sidebar, each clickable.

    Args:
        term: The currently selected Term.
        terms_by_slug: Complete slug-to-Term mapping for lookups.
    """
    related_slugs = term.related_terms[:4]
    if not related_slugs:
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("Related Terms")

    for slug in related_slugs:
        related = terms_by_slug.get(slug)
        if related is None:
            continue
        _render_related_card(related, term.slug)


def _render_related_card(related: Term, current_slug: str) -> None:
    """Render a compact related term card with click-to-navigate.

    Args:
        related: The related Term to display.
        current_slug: Slug of the currently viewed term (for history).
    """
    short_def = related.definition[:100]
    if len(related.definition) > 100:
        short_def += "\u2026"

    st.sidebar.caption(short_def)
    if st.sidebar.button(related.term, key=f"related_{related.slug}"):
        st.session_state.term_history = push_term_history(
            st.session_state.get("term_history", []), current_slug
        )
        st.session_state.selected_term = related.slug
        st.rerun()
