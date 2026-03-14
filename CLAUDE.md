# CLAUDE.md — AI Literacy Tutor (Streamlit)

## Project Purpose

A Streamlit-based AI literacy tool for non-technical professionals in the private sector. It presents a curated dictionary of AI/ML terms with plain-language definitions, real-world examples, and "use in a sentence" guidance. The goal is confident comprehension, not technical mastery.

---

## What This Project Is NOT

Do not over-engineer. This project intentionally excludes:
- LLM-generated or dynamic definitions (all content is static and human-authored)
- User authentication or accounts
- A database (all data lives in flat files)
- An admin UI for editing terms
- Deployment infrastructure (local/Streamlit Community Cloud only)

If a new feature seems to require any of the above, flag it for discussion rather than implementing it.

---

## Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| UI | `streamlit` | Only UI framework; no Flask, FastAPI, etc. |
| Fuzzy Search | `rapidfuzz` | Do NOT use `fuzzywuzzy` (deprecated) |
| Data Format | JSON (`.json`) | Human-editable; one file per category |
| Styling | Streamlit native + optional `st.markdown` CSS | No external CSS frameworks |
| Python Version | 3.11+ | Use type hints throughout |
| Package Manager | `pip` with `requirements.txt` | No Poetry, no conda |

---

## Project Structure

```
ai-tutor/
├── CLAUDE.md                  ← this file
├── README.md
├── requirements.txt
├── app.py                     ← Streamlit entry point (thin orchestration layer only)
│
├── data/
│   ├── _schema.json           ← canonical schema for a term entry (reference only)
│   ├── ml_fundamentals.json
│   ├── neural_networks.json
│   ├── nlp.json
│   ├── computer_vision.json
│   ├── mlops.json
│   └── statistics.json
│
├── core/
│   ├── __init__.py
│   ├── loader.py              ← loads and validates all JSON data at startup
│   ├── search.py              ← fuzzy matching logic (rapidfuzz)
│   └── models.py             ← Pydantic models for Term and Category
│
├── ui/
│   ├── __init__.py
│   ├── sidebar.py             ← category dropdown + search input
│   ├── term_card.py           ← renders a single term's full detail view
│   └── related_panel.py      ← "related terms" sidebar panel
│
└── tests/
    ├── test_loader.py
    ├── test_search.py
    └── test_models.py
```

**Rule:** `app.py` must stay thin — it only calls `ui/` functions. All logic belongs in `core/`.

---

## Data Schema

Every term entry must conform to this shape (see `data/_schema.json`):

```json
{
  "term": "Supervised Learning",
  "slug": "supervised-learning",
  "category": "ml_fundamentals",
  "difficulty": "beginner",
  "definition": "A type of machine learning where a model is trained on labeled data — meaning each training example has a known correct answer.",
  "analogy": "Like a student learning from a textbook with an answer key. The model studies examples where the right answer is already provided.",
  "use_in_a_sentence": "Our team used supervised learning to train a model that predicts customer churn based on historical account data.",
  "business_context": "Common in fraud detection, customer segmentation, and demand forecasting.",
  "related_terms": ["unsupervised-learning", "training-data", "label"],
  "tags": ["core", "model-training"]
}
```

**Field rules:**
- `slug`: lowercase, hyphen-separated, unique across ALL categories
- `difficulty`: one of `"beginner"`, `"intermediate"`, `"advanced"`
- `related_terms`: references slugs (not display names) — enforce this at load time
- `definition`: plain English, no jargon without a link to another term
- `analogy`: required — must use a non-technical reference
- `use_in_a_sentence`: must be a realistic private-sector business scenario

---

## Core Logic

### `core/loader.py`

- Load all `.json` files from `data/` at startup (skip `_schema.json`)
- Validate every entry against the Pydantic `Term` model — raise `ValueError` with the offending slug on failure
- Build two lookup structures:
  - `terms_by_slug: dict[str, Term]` — O(1) lookup
  - `terms_by_category: dict[str, list[Term]]` — for dropdown population
- Cache with `@st.cache_data` so it only runs once per session

### `core/search.py`

- Use `rapidfuzz.process.extractOne` for single best-match search
- Use `rapidfuzz.process.extract` (top 5) for "did you mean?" suggestions
- Search against both `term` (display name) and `tags` fields
- Return `None` if best match score < 60 (configurable constant `MIN_MATCH_SCORE = 60`)
- Never search across slugs directly — slugs are internal only

### `core/models.py`

- Define `Term` and `Category` as Pydantic v2 `BaseModel` classes
- `Term` validator: confirm all `related_terms` slugs exist in the full term index (inject index at validation time)

---

## UI Behavior

### Sidebar (`ui/sidebar.py`)
1. Category dropdown — "All Categories" as default option
2. Text input for term search (label: "Search for a term…")
3. As user types, show top 3 fuzzy suggestions below the input using `st.caption`
4. A "Clear" button that resets both inputs

### Term Card (`ui/term_card.py`)
Render in this order:
1. Term name (`st.title`) + difficulty badge (color-coded `st.badge` or colored `st.markdown`)
2. Category chip
3. Definition (`st.write`)
4. Analogy block — use `st.info` with a 💡 prefix
5. "Use in a sentence" — use `st.success` with a 💼 prefix
6. Business context — use `st.write` with subtle styling
7. Tags as `st.chips` or pill-style `st.markdown` badges

### Related Terms Panel (`ui/related_panel.py`)
- Rendered in `st.sidebar` below the search inputs
- Shows up to 4 related term cards (term name + one-line definition only)
- Each is clickable and sets the selected term in `st.session_state`

---

## Session State Keys

Use these exact keys — do not invent new ones without updating this list:

| Key | Type | Purpose |
|---|---|---|
| `selected_term` | `str \| None` | Slug of currently displayed term |
| `selected_category` | `str \| None` | Currently active category filter |
| `search_query` | `str` | Current text in the search box |

---

## Coding Conventions

- **Type hints everywhere** — no untyped function signatures
- **Docstrings** on all public functions — one-line summary + Args/Returns
- **No global mutable state** outside of `st.session_state`
- **No hardcoded strings** in UI — all display text goes through a `constants.py` file (create if needed)
- **Error handling:** if a term lookup fails, show `st.warning("Term not found. Try a different search.")` — never a raw exception
- Maximum function length: **40 lines** — split if longer
- Use `pathlib.Path` for all file paths, never `os.path`

---

## Initial Categories & Seed Terms

Populate at least 5 terms per category before considering the MVP complete.

| Category File | Display Name | Example Terms |
|---|---|---|
| `ml_fundamentals.json` | ML Fundamentals | Supervised Learning, Model, Feature, Label, Training Data, Inference |
| `neural_networks.json` | Neural Networks | Neuron, Layer, Weight, Bias, Activation Function, Backpropagation |
| `nlp.json` | Natural Language Processing | Tokenization, Embedding, Transformer, Prompt, Fine-tuning |
| `computer_vision.json` | Computer Vision | Image Classification, Object Detection, Convolutional Layer, Pixel |
| `mlops.json` | MLOps & Deployment | Model Drift, Pipeline, Endpoint, Monitoring, A/B Testing |
| `statistics.json` | Statistics & Math | Mean, Variance, Distribution, Correlation, Overfitting, Underfitting |

---

## Requirements File

```
streamlit
rapidfuzz
pydantic
pytest
```

---

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Testing

- Tests live in `tests/` and use `pytest`
- Run with: `pytest tests/ -v`
- Required test coverage:
  - `test_loader.py`: valid JSON loads without error; invalid schema raises `ValueError`
  - `test_search.py`: exact match returns score 100; gibberish returns `None`; partial match returns correct term
  - `test_models.py`: missing required fields raise Pydantic `ValidationError`
- Do not use mocks for the data loader — use a small `fixtures/` JSON file instead

---

## MVP Definition of Done

The MVP is complete when:
- [ ] All 6 category JSON files have ≥ 5 valid terms each
- [ ] Category dropdown filters the search scope correctly
- [ ] Fuzzy search returns the correct term for partial/misspelled input
- [ ] Term card renders all 7 fields without layout breakage
- [ ] Related terms panel updates when a new term is selected
- [ ] All `pytest` tests pass
- [ ] App runs with `streamlit run app.py` from a clean `pip install`

---

## Out of Scope (Do Not Implement)

- Quiz/flashcard mode (future phase)
- User progress tracking
- PDF export of definitions
- Admin interface for adding terms
- Any LLM API calls
- Login or access control