"""AI Literacy Tutor — Streamlit entry point."""

import streamlit as st

from core.constants import APP_TITLE, TERM_NOT_FOUND_MSG
from core.loader import load_all_terms
from core.search import search_best_match
from ui.related_panel import render_related_panel
from ui.sidebar import render_sidebar
from ui.term_card import render_term_card
from ui.welcome import render_welcome_page

st.set_page_config(page_title=APP_TITLE, layout="wide")

terms_by_slug, terms_by_category = load_all_terms()

# Permalink: load term from URL on initial visit
url_term = st.query_params.get("term")
if url_term and url_term in terms_by_slug:
    if "selected_term" not in st.session_state:
        st.session_state.selected_term = url_term

render_sidebar(terms_by_slug, terms_by_category)

# If user typed a search but hasn't clicked a suggestion, auto-select best match
query = st.session_state.get("search_query", "")
selected = st.session_state.get("selected_term")

if query.strip() and not selected:
    match = search_best_match(
        query,
        terms_by_slug,
        category_filter=st.session_state.get("selected_category"),
    )
    if match:
        st.session_state.selected_term = match.slug
        selected = match.slug

# Main content area
if selected and selected in terms_by_slug:
    term = terms_by_slug[selected]
    render_term_card(term, terms_by_slug)
    render_related_panel(term, terms_by_slug)
    st.query_params["term"] = selected
elif selected:
    st.warning(TERM_NOT_FOUND_MSG)
else:
    if "term" in st.query_params:
        del st.query_params["term"]
    render_welcome_page(terms_by_slug, terms_by_category)
