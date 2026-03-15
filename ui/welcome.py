"""Welcome page with search hero, quick-start terms, and suggestion form."""

import os

import streamlit as st

from core.constants import (
    CATEGORY_DISPLAY_NAMES,
    QUICK_START_SLUGS,
    SUGGEST_ERROR_MSG,
    SUGGEST_RATE_LIMIT_MSG,
    SUGGEST_SUCCESS_MSG,
    SUGGEST_TERM_HEADING,
    SUGGEST_TERM_SUBTEXT,
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


def _render_suggestion_form() -> None:
    """Render the term suggestion form with rate limiting."""
    if "suggestion_submitted" not in st.session_state:
        st.session_state.suggestion_submitted = False

    st.markdown("---")
    st.subheader(SUGGEST_TERM_HEADING)
    st.write(SUGGEST_TERM_SUBTEXT)

    if st.session_state.suggestion_submitted:
        st.info(SUGGEST_RATE_LIMIT_MSG)
        return

    if not os.environ.get("GITHUB_TOKEN"):
        return

    _render_suggestion_fields()


def _render_suggestion_fields() -> None:
    """Render the form fields and handle submission."""
    from core.github_api import create_issue
    from core.sanitize import (
        build_issue_body,
        sanitize_context,
        sanitize_term_name,
    )

    with st.form("suggest_term_form"):
        term_name = st.text_input("Term Name *", max_chars=100)
        category = st.selectbox(
            "Suggested Category",
            options=list(CATEGORY_DISPLAY_NAMES.keys()),
            format_func=lambda k: CATEGORY_DISPLAY_NAMES[k],
        )
        difficulty = st.radio(
            "Difficulty",
            options=["beginner", "intermediate", "advanced"],
            horizontal=True,
        )
        context = st.text_area(
            "Additional Context (optional)",
            max_chars=1000,
            placeholder="Why is this term useful? Any definition you'd suggest?",
        )
        submitted = st.form_submit_button("Submit Suggestion")

    if not submitted:
        return

    _handle_submission(term_name, category, difficulty, context)


def _handle_submission(
    term_name: str,
    category: str,
    difficulty: str,
    context: str,
) -> None:
    """Validate, sanitize, and submit the suggestion.

    Args:
        term_name: Raw term name from form.
        category: Selected category key.
        difficulty: Selected difficulty level.
        context: Optional context text.
    """
    from core.github_api import create_issue
    from core.sanitize import (
        build_issue_body,
        sanitize_context,
        sanitize_term_name,
    )

    try:
        clean_name = sanitize_term_name(term_name)
    except ValueError:
        st.error("Please enter a valid term name.")
        return

    clean_context = sanitize_context(context)
    body = build_issue_body(clean_name, category, difficulty, clean_context)

    try:
        result = create_issue(
            title=f"Term Suggestion: {clean_name}",
            body=body,
        )
        st.success(SUGGEST_SUCCESS_MSG)
        st.markdown(f"[View your suggestion on GitHub]({result['html_url']})")
        st.session_state.suggestion_submitted = True
    except RuntimeError:
        st.error(SUGGEST_ERROR_MSG)


def render_welcome_page(
    terms_by_slug: dict[str, Term],
    terms_by_category: dict[str, list[Term]],
) -> None:
    """Render the landing page with search, quick-starts, and suggestion form.

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

    _render_suggestion_form()
