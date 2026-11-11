"""Streamlit-facing wrapper around the pure data_loading module.

The pure logic lives in `core.data_loading` so the GitHub Action and CLI
tool can import it without pulling Streamlit into their dependency chain.
"""

import streamlit as st

from core.data_loading import (
    DATA_DIR,
    compute_category_difficulty_counts,
    compute_term_counts,
    get_category_display_name,
    load_all_terms_impl,
)
from core.models import Term

# Backwards-compatible alias used by tests that still monkeypatch the
# module-level DATA_DIR.
_load_all_terms_impl = load_all_terms_impl

__all__ = [
    "DATA_DIR",
    "compute_category_difficulty_counts",
    "compute_term_counts",
    "get_category_display_name",
    "load_all_terms",
    "_load_all_terms_impl",
]


@st.cache_resource
def load_all_terms() -> tuple[dict[str, Term], dict[str, list[Term]]]:
    """Cached wrapper that loads all terms once per Streamlit session.

    Returns:
        A tuple of (terms_by_slug, terms_by_category).
    """
    return load_all_terms_impl()
