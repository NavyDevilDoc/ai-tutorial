# PROGRESS.md — AI Literacy Tutor Development Record

## Session: 2026-03-14

### Overview

Built a complete Streamlit-based AI literacy tool from scratch in a single session. The app presents a curated glossary of 112 AI/ML terms with plain-language definitions, analogies, business context, and related-term navigation — designed for non-technical professionals in the private sector.

---

### Phase 1: Project Foundation

**Goal:** Establish the project skeleton, data models, and tooling.

**What was built:**
- Project structure: `core/`, `ui/`, `data/`, `tests/` directories
- `core/models.py` — Pydantic v2 `Term` and `Category` models with slug validation and cross-reference checking
- `core/constants.py` — All display strings, difficulty colors, category display names
- `data/_schema.json` — Reference schema for term entries
- `requirements.txt` with streamlit, rapidfuzz, pydantic, pytest

**Key design decisions:**
- Related-terms cross-validation happens post-load in `loader.py`, not in the Pydantic model (avoids chicken-and-egg at construction time)
- Slug format enforced via regex: `^[a-z0-9]+(-[a-z0-9]+)*$`

---

### Phase 2: Seed Data — Initial 34 Terms

**Goal:** Populate all 6 original categories with minimum 5 terms each.

**Categories and initial term counts:**
| Category | Terms |
|---|---|
| ML Fundamentals | 7 |
| Neural Networks | 6 |
| NLP | 5 |
| Computer Vision | 5 |
| MLOps & Deployment | 5 |
| Statistics & Math | 6 |
| **Total** | **34** |

**Authoring approach:** All slugs planned upfront in a master list before writing any JSON, ensuring cross-references were valid from the start.

---

### Phase 3: Core Logic

**Goal:** Build the data loading pipeline and fuzzy search.

**What was built:**
- `core/loader.py` — Loads all JSON from `data/`, validates with Pydantic, builds `terms_by_slug` and `terms_by_category` dicts. Split into `_load_all_terms_impl()` (pure, testable) + `load_all_terms()` (`@st.cache_resource` wrapper)
- `core/search.py` — Fuzzy matching via `rapidfuzz.process.extractOne` and `.extract`. Searches against concatenated term name + tags. `MIN_MATCH_SCORE = 60`

**Key design decisions:**
- `@st.cache_resource` instead of `@st.cache_data` to avoid Pydantic serialization issues
- Search builds `{slug: "term_name tag1 tag2"}` dict for rapidfuzz, enabling both name and tag matching

---

### Phase 4: UI Components + App Entry Point

**Goal:** Build all UI modules and the thin `app.py` orchestrator.

**What was built:**
- `ui/sidebar.py` — Category dropdown, search input with fuzzy suggestions, clear button
- `ui/term_card.py` — Full term detail view (title, difficulty badge, definition, analogy, sentence, business context, tags)
- `ui/related_panel.py` — Up to 4 clickable related terms in the sidebar
- `app.py` — Thin orchestrator wiring everything together

**Session state keys established:** `selected_term`, `selected_category`, `search_query`

---

### Phase 5: Initial Test Suite — 18 Tests

**Goal:** Comprehensive test coverage for core logic.

**What was built:**
- `tests/test_models.py` (10 tests) — Pydantic validation, slug format, difficulty constraints, cross-references
- `tests/test_loader.py` (4 tests) — Valid load, invalid schema, dangling refs, schema file skip
- `tests/test_search.py` (6 tests) — Exact match, partial/typo match, gibberish, suggestions, category filter, tag search
- `tests/fixtures/valid_terms.json` and `invalid_terms.json`

**Design:** Tests use real fixture files, not mocks. Loader tests use `monkeypatch` to inject temp data directories.

---

### Phase 6: uv Setup

**Goal:** Replace pip with uv for virtual environment and dependency management.

**What was done:**
- `uv init` created `pyproject.toml` and `.venv`
- `uv add` installed runtime and dev dependencies
- Added `[tool.pytest.ini_options] pythonpath = ["."]` to fix module resolution in the uv venv

**Commands:** `uv run streamlit run app.py` and `uv run pytest tests/ -v`

---

### Phase 7: UX Feedback — Difficulty Filter + Tag Fix

**Goal:** Address first round of user testing feedback.

**Changes:**
1. **Tag pill text color** — Added `color:black` to tag badges for dark mode readability
2. **Difficulty radio buttons** — Added horizontal radio filter (All Levels / Beginner / Intermediate / Advanced) with `selected_difficulty` session state key
3. **Term browser dropdown** — Added "Browse terms..." selectbox between category dropdown and search box, filtered by both category and difficulty

---

### Phase 8: Content Expansion — 34 to 99 Terms

**Goal:** Triple the glossary with high-value terms and 3 new categories.

**Existing categories expanded:**
| Category | Before | After |
|---|---|---|
| ML Fundamentals | 7 | 16 |
| Neural Networks | 6 | 11 |
| NLP | 5 | 13 |
| Computer Vision | 5 | 10 |
| MLOps & Deployment | 5 | 12 |
| Statistics & Math | 6 | 13 |

**New categories created:**
| Category | Terms | Rationale |
|---|---|---|
| Generative AI | 8 | LLMs, RAG, agents, guardrails — the boardroom buzzwords |
| AI Ethics & Governance | 8 | Bias, explainability, privacy — legal/compliance demand |
| Business & Strategy | 8 | ROI, POC, human-in-the-loop — bridges tech and exec conversations |

**Notable additions:** Large Language Model, Hallucination, RAG, AI Agent, Guardrails, Algorithmic Bias, Explainability, ROI of AI, Human-in-the-Loop, Total Cost of Ownership

---

### Phase 9: Six UI Improvements — 18 to 32 Tests

**Goal:** Enhance discoverability and usability based on the target audience's needs.

#### 9a: Theme-Safe Styling
- Replaced hardcoded `color:black`, `color:white`, `#e0e0e0` with CSS classes using `rgba()` values
- Added `_inject_card_styles()` with a single `<style>` block defining `.difficulty-badge-*` and `.tag-pill` classes
- Works correctly in both Streamlit light and dark themes

#### 9b: Term Count Badges on Filters
- Category dropdown now shows "ML Fundamentals (24)" with `format_func` on `st.selectbox`
- Difficulty radio shows "Beginner (53)" with `format_func` on `st.radio`
- Added `compute_term_counts()` to `core/loader.py` — pure function, tested
- Refactored sidebar to use raw keys as options + `format_func` for display, eliminating `_get_category_key()` and `_get_difficulty_key()` helpers
- Created `tests/conftest.py` with shared fixtures for all subsequent test phases
- Enriched `tests/fixtures/valid_terms.json` to 4 terms across 2 categories with mixed difficulties

#### 9c: Welcome Page with Category Cards
- Created `ui/welcome.py` with a 3x3 grid of clickable category cards
- Each card: category name, term count, difficulty distribution, sample term, "Explore" button
- Added `compute_category_difficulty_counts()` to `core/loader.py`
- Replaced blank landing page in `app.py` with `render_welcome_page()`

#### 9d: Permalink / Share a Term
- URLs like `?term=hallucination` now load that term directly
- Uses `st.query_params` — reads on initial visit, updates on navigation
- Added URL-safety smoke test validating all 112 slugs

#### 9e: Back Navigation / Breadcrumb
- Created `core/navigation.py` with pure `push_term_history()` and `pop_term_history()` functions
- History stack (max depth 10) tracks related-term navigation
- Back button appears with previous term name when history exists
- Created `tests/test_navigation.py` with 6 tests (push, pop, max depth, empty, no-op)

#### 9f: Alphabet Grouping in Browse Dropdown
- Added letter selector radio (A-Z, horizontal) that filters the browse dropdown
- Added `get_available_letters()` and `group_terms_by_letter()` to `core/search.py`
- Created `tests/test_browse.py` with 4 tests

---

### Phase 10: Navigation Overhaul

**Goal:** Fix fundamental UX issues identified during hands-on user testing.

**Problems identified:**
1. Explore buttons on landing page set category but didn't clear previous term selection
2. No Home button — users relied on "Clear" to navigate back
3. Landing page duplicated sidebar categories in a cluttered 3x3 grid
4. No intuitive way to get from a term page back to the starting point

**Solutions implemented:**

#### Landing page redesign (`ui/welcome.py`)
- Replaced category card grid with a search-forward hero section
- Prominent heading: "What do you want to learn about?"
- Search box with placeholder examples
- 6 curated quick-start term buttons (LLM, Hallucination, Supervised Learning, Overfitting, RAG, A/B Testing)
- Subtle footer with total term/category count

#### Navigation buttons (`ui/term_card.py`)
- Added **Home** button at top of every term view — clears selection and returns to landing page
- **Back** button appears next to Home when navigation history exists
- Buttons laid out in columns for clean alignment

#### Sidebar cleanup (`ui/sidebar.py`)
- Renamed "Clear" to "Reset Filters" (more accurate label)

---

### Phase 11: Streamlit Event-Driven Bug Fixes

**Goal:** Fix button/widget interactions that appeared correct in code but failed at runtime.

#### Bug: Buttons not navigating (Home, Back, Quick Starts, Related Terms)
- **Root cause:** Setting `st.session_state.selected_term = slug` inside a button callback only takes effect on the next rerun. Without `st.rerun()`, the current run finishes rendering the old page.
- **Fix:** Added `st.rerun()` after every button-driven state change in `term_card.py`, `related_panel.py`, `welcome.py`, and `sidebar.py`

#### Bug: Browse dropdown not navigating to selected term
- **Root cause:** Selectboxes persist their value across reruns (unlike buttons which are momentary). Calling `st.rerun()` after a selectbox change created an infinite rerun loop — select term → set state → rerun → selectbox still has term selected → set state again → rerun. Streamlit's rerun protection killed the cycle silently.
- **Fix:** Replaced inline check-and-rerun pattern with an `on_change` callback + `key`. The callback sets `selected_term` and resets the dropdown back to its placeholder, breaking the loop.

#### Bug: "RAG" search returning wrong term
- **Root cause:** Short acronyms (3 chars) don't produce reliable fuzzy matches against full term names. The full query "retrieval-augmented generation" already matched correctly (score 81.0).
- **Fix:** Added acronym tags ("RAG", "LLM", "NER") to relevant terms so short-form searches work via tag matching.

**Key learning:** Streamlit buttons and selectboxes have fundamentally different lifecycles. Buttons need `st.rerun()` to force navigation. Selectboxes must NOT use `st.rerun()` — use `on_change` callbacks instead.

---

### Phase 12: Model Catalog Expansion — 99 to 112 Terms

**Goal:** Add specific ML model types and neural network architectures at the "what it does and when to use it" level.

**New ML model terms (8):**
| Term | Difficulty | Tag |
|---|---|---|
| Logistic Regression | intermediate | classification-model |
| Decision Tree | intermediate | classification-model, interpretable |
| Random Forest | intermediate | classification-model, ensemble |
| Support Vector Machine | intermediate | classification-model, SVM |
| K-Nearest Neighbors | intermediate | classification-model, kNN |
| Naive Bayes | intermediate | classification-model, text-classification |
| Ensemble Method | intermediate | technique |
| Gradient Boosting | advanced | ensemble, XGBoost |

**New neural network architecture terms (5):**
| Term | Difficulty | Use Case |
|---|---|---|
| Convolutional Neural Network (CNN) | intermediate | Image/video processing |
| Recurrent Neural Network (RNN) | intermediate | Sequential data, time series |
| LSTM | advanced | Long-range pattern detection |
| Generative Adversarial Network (GAN) | advanced | Synthetic image generation |
| Autoencoder | advanced | Anomaly detection, compression |

**Editorial guideline followed:** Every definition stays at the "meeting-ready" level. The litmus test: Would a product manager need this to have an informed conversation with their data science team?

---

### Phase 13: Security Review & Hardening

**Goal:** Audit the codebase for vulnerabilities before pushing to a public GitHub repo.

**Findings and fixes:**

| Finding | Severity | Action Taken |
|---|---|---|
| XSS in tag rendering — `tags` from JSON injected into `unsafe_allow_html` without escaping | HIGH | Added `html.escape()` to both `_render_tags()` and `_render_difficulty_badge()` in `ui/term_card.py` |
| `.gitignore` missing `.env`, `*.key`, `*.pem`, `*.log` entries | Low | Added all missing patterns |
| `requirements.txt` redundant with `pyproject.toml` | Low | Removed, then re-added with pinned versions matching `pyproject.toml` for Railway compatibility |
| Removed stale `main.py` stub left over from `uv init` | Low | Deleted |

**No credentials, API keys, or PII found anywhere in the codebase.**

---

### Phase 14: GitHub Repository & Railway Deployment

**Goal:** Push to public GitHub and deploy to Railway.

**What was done:**
- Created public GitHub repo: `NavyDevilDoc/ai-tutorial`
- Initial commit with all 39 files (4,463 lines)
- Created `Procfile` for Railway: `web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
- `requirements.txt` with pinned versions for Railway's Python buildpack
- Deployed to Railway via dashboard (GitHub repo connection)
- Verified live environment matches local behavior

---

### Phase 15: Term Authoring CLI (Stage 1 of Content Pipeline)

**Goal:** Build a repeatable, validated workflow for adding new terms — with an eye toward future automation.

**What was built:** `tools/add_term.py` — a CLI tool with three operating modes:

1. **LLM-assisted** (default when `ANTHROPIC_API_KEY` is set):
   - Requires only 3 inputs: term name, category, difficulty
   - Loads 3 existing terms from the target category as few-shot examples
   - Calls Claude Sonnet to generate the full 10-field entry matching the glossary's style
   - Human reviews → approve / edit individual fields / regenerate / cancel

2. **Manual** (`--no-llm` flag or no API key):
   - Interactive prompts for all 10 fields with validation hints

3. **Automated** (`--json-file path`):
   - Accepts a pre-built JSON file — the pipeline entry point for Stages 2-3
   - Validates and appends without interactive prompts

**Validation guarantees (all modes):**
- Pydantic `Term` model validation (all required fields, slug format, difficulty literal)
- Slug uniqueness check against all existing 113 terms
- Related-terms cross-reference warnings for dangling slugs
- Refuses to write if validation fails

**Dependencies added:** `anthropic>=0.84.0` as a dev dependency (not deployed to Railway)

**Test:** Added "Compute" term to `ml_fundamentals.json` via the `--json-file` mode, verified all 32 tests pass.

**Automation architecture for Stages 2-3:**
- Stage 2: Streamlit form in app → creates GitHub Issue with structured JSON body (requires GitHub token)
- Stage 3: GitHub Action on `term-approved` label → extracts JSON → runs `tools/add_term.py --json-file` → opens PR
- Human-in-the-loop: two approval gates (add label + merge PR)
- Full chain: User suggests in app → GitHub Issue → Label → Action runs CLI → PR → Merge → Railway auto-deploys

---

## Final Project State

### Codebase

| Layer | Files |
|---|---|
| Entry point | `app.py` |
| Core logic | `core/models.py`, `core/loader.py`, `core/search.py`, `core/navigation.py`, `core/constants.py` |
| UI | `ui/sidebar.py`, `ui/term_card.py`, `ui/related_panel.py`, `ui/welcome.py` |
| Tooling | `tools/add_term.py` |
| Tests | `tests/conftest.py`, `tests/test_models.py`, `tests/test_loader.py`, `tests/test_search.py`, `tests/test_navigation.py`, `tests/test_browse.py` |
| Data | 9 category JSON files + `_schema.json` |
| Config | `pyproject.toml`, `requirements.txt`, `Procfile`, `CLAUDE.md`, `README.md` |

### Content

| Metric | Count |
|---|---|
| Total terms | 113 |
| Categories | 9 |
| Beginner terms | 54 |
| Intermediate terms | 51 |
| Advanced terms | 8 |

### Tests

| Test File | Tests | What It Covers |
|---|---|---|
| test_models.py | 10 | Pydantic validation, slug format, difficulty, cross-refs |
| test_loader.py | 8 | Data loading, validation, counts, difficulty distribution, URL safety |
| test_search.py | 6 | Exact match, fuzzy match, gibberish, suggestions, category filter, tag search |
| test_navigation.py | 6 | History push, pop, max depth, empty stack, no-op |
| test_browse.py | 4 | Letter grouping, available letters, sorting, empty input |
| **Total** | **32** | |

### Tech Stack

| Layer | Choice |
|---|---|
| UI | Streamlit |
| Fuzzy search | rapidfuzz |
| Data validation | Pydantic v2 |
| Data format | JSON (one file per category) |
| Term generation | Anthropic Claude API (dev tooling only) |
| Testing | pytest |
| Package management | uv |
| Hosting | Railway (via GitHub integration) |
| Source control | GitHub (`NavyDevilDoc/ai-tutorial`) |
| Python | 3.12+ |

### Features Implemented

- Category dropdown with term counts
- Difficulty radio filter with term counts
- Alphabetical letter selector + filtered term dropdown
- Fuzzy search with tag matching and acronym support
- Term detail card (definition, analogy, use-in-a-sentence, business context, tags)
- Related terms panel with click-to-navigate
- Back navigation with history stack (max depth 10)
- Home button on every term page
- Welcome page with hero search and quick-start terms
- Permalink support (`?term=slug` in URL)
- Theme-safe styling (light + dark mode)

### Features Implemented (Tooling)

- CLI term authoring tool with LLM-assisted generation
- Few-shot prompting with existing terms as style examples
- JSON file import mode for pipeline automation
- Pydantic validation, slug uniqueness, and cross-reference checking on every write

### Out of Scope (Documented for Future)

- Quiz/flashcard mode
- User progress tracking
- PDF export
- Admin interface for editing terms
- Authentication

### Planned Next (Stages 2-3 of Content Pipeline)

- In-app term suggestion form → GitHub Issue (Stage 2)
- GitHub Action for automated PR creation from approved suggestions (Stage 3)
