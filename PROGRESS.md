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
- Slug uniqueness check against all existing terms
- Related-terms cross-reference warnings for dangling slugs
- Refuses to write if validation fails

**Dependencies added:** `anthropic>=0.84.0` as a dev dependency (not deployed to Railway)

**Initial test:** Added "Compute" term to `ml_fundamentals.json` via the `--json-file` mode, verified all 32 tests pass.

**Automation architecture for Stages 2-3:**
- Stage 2: Streamlit form in app → creates GitHub Issue with structured JSON body (requires GitHub token)
- Stage 3: GitHub Action on `term-approved` label → extracts JSON → runs `tools/add_term.py --json-file` → opens PR
- Human-in-the-loop: two approval gates (add label + merge PR)
- Full chain: User suggests in app → GitHub Issue → Label → Action runs CLI → PR → Merge → Railway auto-deploys

---

### Phase 16: First Batch Content Generation via CLI (114 → 129 Terms)

**Goal:** Validate the CLI pipeline at scale by generating and adding 16 new terms using LLM-assisted authoring.

**Terms added:**

| Category | New Terms |
|---|---|
| ML Fundamentals (+7) | Hyperparameter, Clustering, Benchmark, Ground Truth, Feature Engineering, Data Labeling, Compute |
| NLP (+7) | GPT, Prompt Engineering, Temperature, Few-Shot Learning, Zero-Shot Learning, Semantic Search, Knowledge Graph, Natural Language Processing |
| Neural Networks (+1) | Attention |
| MLOps (+1) | Edge AI |

**Process:** Each term was generated by calling `generate_term_with_llm()` with few-shot examples from the target category, saved to a temp JSON file, then added via `tools/add_term.py --json-file`. All terms passed Pydantic validation and slug uniqueness checks.

**Acronym tags added:** GPT tag on GPT term for short-form search support (matching the RAG/LLM/NER pattern established earlier).

**Lessons learned — sequential ordering issue:**
When adding terms in sequence, mutual cross-references cause failures. For example, Few-Shot Learning referenced Zero-Shot Learning, which hadn't been added yet. The loader's strict validation (`_validate_all_related_terms`) rejects the entire dataset when any dangling reference exists, which blocks all subsequent additions.

**Workarounds applied:**
1. Pre-stripped dangling `related_terms` from generated JSON files before import (checked against the union of existing + planned slugs)
2. Fixed terms in-place when ordering caused validation failures
3. Restored stripped cross-references after all terms were present

**Recommended improvement for Stage 2:** Add a `--skip-related-validation` flag or a batch-import mode to `tools/add_term.py` that defers cross-reference validation until after all terms in the batch are loaded. This would eliminate the ordering problem entirely.

**Environment setup note:** Windows Notepad adds a UTF-8 BOM (byte order mark) to `.env` files, which breaks `source .env` in bash. The fix is to rewrite the file with `utf-8` encoding (not `utf-8-sig`). The working command for loading the API key on Windows bash: `export $(cat .env | xargs)`.

---

### Phase 17: Stages 2-3 Implementation — Suggestion Pipeline + Security Hardening

**Goal:** Build the full automated content pipeline: user suggests a term in the app → GitHub Issue → maintainer approves → Action generates term → PR created → merge → deploy.

**What was built:**

**Stage 2 — In-App Suggestion Form:**
- `core/sanitize.py` — Input sanitization layer with 3-layer defense (sanitize at form entry, re-sanitize in Action, Pydantic validates before write). Strips HTML tags, control characters, null bytes. Constructs issue body with user input safely escaped via `json.dumps()`.
- `core/github_api.py` — GitHub Issue creation via stdlib `urllib.request` (no new runtime dependencies). Token read from env var, never logged or included in error messages. Tested with mock that verifies token doesn't leak.
- `ui/welcome.py` — Suggestion form at bottom of welcome page. Rate limited to 1 submission per session. Hidden when no `GITHUB_TOKEN` is configured.
- `core/constants.py` — Added suggestion form display strings.

**Stage 3 — GitHub Action Automation:**
- `.github/workflows/term-from-issue.yml` — Triggers on `term-approved` label. Permissions explicitly scoped to `contents:write`, `pull-requests:write`, `issues:write`.
- `.github/scripts/process_approved_term.py` — Extracts JSON from issue body (regex), re-sanitizes all fields as untrusted input, generates full term via Claude few-shot prompting, validates with Pydantic, strips dangling related_terms, appends to JSON file. Creates branch and PR.

**Security hardening:**
- Branch renamed `master` → `main` (modern convention)
- Branch protection on `main` (initially required 1 approving review; relaxed for solo developer)
- GitHub Fine-Grained PAT scoped to `NavyDevilDoc/ai-tutorial` with Issues R/W only
- `ANTHROPIC_API_KEY` stored as GitHub Actions secret
- `GITHUB_TOKEN` PAT stored as Railway environment variable
- Safe error logging with automatic API key prefix redaction
- 22 new tests covering sanitization, GitHub API, and Action script logic

**Tests added:** 32 → 54

---

### Phase 18: Live Pipeline Debugging (The Gauntlet)

**Goal:** Get the full pipeline working end-to-end in production.

This phase was entirely debugging — every component worked in isolation but the live integration surfaced a chain of issues that had to be resolved sequentially.

**Issue 1: Railway deployment failed — `refs/heads/master` not found**
- **Cause:** Railway was configured to deploy from `master`, which we renamed to `main`.
- **Fix:** Updated Railway service settings to deploy from `main`.

**Issue 2: Suggestion form returned "Something went wrong"**
- **Cause:** The GitHub Fine-Grained PAT was created without the Issues permission. The GitHub permissions UI for fine-grained tokens is non-obvious — the "Read and write" toggle only appears after checking the "Issues" checkbox in a nested dropdown under "+ Add permissions".
- **Fix:** Created a new PAT with correct Issues R/W scope, updated Railway `GITHUB_TOKEN` variable.

**Issue 3: GitHub labels not visible in issue UI**
- **Cause:** Labels created via `gh label create` CLI were not appearing in the GitHub web UI label dropdown. Recreating via the REST API (`gh api repos/.../labels --method POST`) fixed the issue.
- **Fix:** Deleted and recreated both `term-suggestion` and `term-approved` labels via the API.

**Issue 4: GitHub Action triggered but skipped**
- **Cause:** The `if: github.event.label.name == 'term-approved'` condition didn't match because the label wasn't actually persisting on the issue (UI issue — checking the box and clicking away didn't save). Applied labels via CLI instead.
- **Fix:** Used `gh issue edit --add-label` to apply labels reliably.

**Issue 5: Action failed — `ModuleNotFoundError: No module named 'streamlit'`**
- **Cause:** The workflow installed `pydantic anthropic rapidfuzz` but not `streamlit`. The `core/loader.py` imports `streamlit` for the `@st.cache_resource` decorator, even though the Action only uses the pure loading logic.
- **Fix:** Added `streamlit` to the Action's `pip install` step.

**Issue 6: Action failed — "GitHub Actions is not permitted to create or approve pull requests"**
- **Cause:** The repository's Actions settings didn't allow the workflow to create PRs. This is a separate setting from the workflow's `permissions` block.
- **Fix:** Enabled via `gh api repos/.../actions/permissions/workflow --method PUT` with `can_approve_pull_request_reviews=true` and `default_workflow_permissions="write"`.

**Issue 7: Action failed — `error: failed to push some refs`**
- **Cause:** The branch `auto/term-from-issue-2` already existed from a previous failed run. Git refused to push to an existing remote branch.
- **Fix:** Deleted the stale branch with `git push origin --delete auto/term-from-issue-2` and re-triggered.

**Issue 8: Branch protection blocked our own fixes**
- **Cause:** We set "require 1 approving review" on `main`, but as a solo developer you can't review your own PRs.
- **Fix:** Relaxed branch protection to remove the review requirement while keeping force-push and deletion protections.

**Resolution:** After fixing all 8 issues, the pipeline completed successfully:
- "Hallucination Rate" suggested via the app → Issue #2 created → `term-approved` label added → Action generated term → PR #4 created → merged → Railway deployed.
- "Explainable AI" submitted as a second test → Issue #3 → Action → PR → merged → deployed.

**Key takeaway:** The architecture was sound — every component (sanitization, API calls, Action script, term generation, validation) worked correctly. The failures were all integration and permissions issues that only surface in a live environment. This is typical of CI/CD pipeline first-time setup.

---

### Phase 19: Documentation — ADD_A_TERM.md

**Goal:** Formalize the three methods for adding terms into a single reference document.

**What was created:** `ADD_A_TERM.md` covering:
1. **Method 1: App suggestion form** — step-by-step for end users
2. **Method 2: Label-based approval** — step-by-step for maintainers, including troubleshooting
3. **Method 3: CLI tool** — all four modes (interactive LLM, manual, with args, JSON import)
4. **Term schema reference** — all 10 fields with validation rules
5. **Valid categories table**

---

### Phase 20: Term Relationship Graph + Batch Import Mode

**Goal:** Two feature additions — an interactive network graph showing how terms connect, and a batch import mode that fixes the sequential ordering problem from Phase 16.

#### Feature 1: Term Relationship Network Graph

**What was built:**
- `core/graph.py` — Pure graph construction logic using networkx. `build_term_graph()` creates a network centered on the selected term with related terms as connected nodes. `get_graph_layout()` computes spring layout positions. `get_node_color()` maps difficulty to hex colors.
- `ui/graph.py` — Plotly rendering inside a collapsible `st.expander("Term Relationships")`. Nodes color-coded by difficulty (green/orange/red), center term displayed larger. Transparent background works in both light and dark themes.
- `ui/term_card.py` — Graph rendered at the bottom of every term card when `terms_by_slug` is available.

**Design decisions:**
- Graph is a **visual map**, not a navigation control. Plotly charts in Streamlit don't support click callbacks natively, so the existing Related Terms sidebar buttons remain the navigation mechanism. The graph supplements by showing the broader relationship picture.
- Rendered inside an expander (collapsed by default) to keep the term card clean for users who just want definitions.
- Used networkx (lightweight, stdlib-style API) + Plotly (already bundled with Streamlit) to minimize new dependencies.

**Dependencies added:** `networkx>=3.0`, `plotly>=6.0`

**Deprecation fix:** Streamlit deprecated `use_container_width` on `st.plotly_chart()` — replaced with `width="stretch"` before pushing.

**Tests:** 7 new tests in `test_graph.py` — center node presence, related node inclusion, edge connections, missing slug handling, empty related terms, layout positions, color mapping.

#### Feature 2: Batch Import Mode for CLI

**What was built:**
- `tools/add_term.py` — New `--batch-dir` flag reads all `.json` files from a directory. `--json-file` now also accepts JSON arrays (not just single objects). Both route to `batch_import()`.
- `batch_import()` — Loads all terms, validates them as a combined set (existing + entire batch), then writes all at once. Atomic: if any term fails validation, nothing is written.
- `_validate_batch()` — Two-pass validation. First pass collects all slugs in the batch. Second pass validates each term against the union of existing + batch slugs. This is what makes mutual cross-references work.
- `validate_term_against(term_data, existing_slugs)` — Refactored from `validate_term()` to accept a pre-loaded slug set, eliminating the per-term disk load that made batch operations expensive. Original `validate_term()` preserved as a backward-compatible wrapper.

**This solves the Phase 16 ordering problem:** Terms that reference each other (e.g., Few-Shot Learning ↔ Zero-Shot Learning) can now be added in a single batch without errors, because the validator sees the complete set before checking any references.

**Tests:** 9 new tests in `test_batch_import.py` — mutual references pass, duplicate-within-batch detected, duplicate-with-existing detected, schema errors caught, atomic rollback verified, directory loading, validate_term_against unit tests.

---

## Final Project State

### Codebase

| Layer | Files |
|---|---|
| Entry point | `app.py` |
| Core logic | `core/models.py`, `core/loader.py`, `core/search.py`, `core/navigation.py`, `core/constants.py`, `core/sanitize.py`, `core/github_api.py` |
| UI | `ui/sidebar.py`, `ui/term_card.py`, `ui/related_panel.py`, `ui/welcome.py` |
| Tooling | `tools/add_term.py` |
| Automation | `.github/workflows/term-from-issue.yml`, `.github/scripts/process_approved_term.py` |
| Tests | `tests/conftest.py`, `tests/test_models.py`, `tests/test_loader.py`, `tests/test_search.py`, `tests/test_navigation.py`, `tests/test_browse.py`, `tests/test_sanitize.py`, `tests/test_github_api.py`, `tests/test_process_approved_term.py` |
| Data | 9 category JSON files + `_schema.json` |
| Config | `pyproject.toml`, `requirements.txt`, `Procfile`, `CLAUDE.md`, `README.md`, `ADD_A_TERM.md` |

### Content

| Metric | Count |
|---|---|
| Total terms | 131 |
| Categories | 9 |
| Beginner terms | 60 |
| Intermediate terms | 63 |
| Advanced terms | 8 |

### Tests

| Test File | Tests | What It Covers |
|---|---|---|
| test_models.py | 10 | Pydantic validation, slug format, difficulty, cross-refs |
| test_loader.py | 8 | Data loading, validation, counts, difficulty distribution, URL safety |
| test_search.py | 6 | Exact match, fuzzy match, gibberish, suggestions, category filter, tag search |
| test_navigation.py | 6 | History push, pop, max depth, empty stack, no-op |
| test_browse.py | 4 | Letter grouping, available letters, sorting, empty input |
| test_sanitize.py | 11 | Text sanitization, HTML stripping, truncation, issue body JSON construction |
| test_github_api.py | 5 | Issue creation, token handling, error messages, header verification |
| test_process_approved_term.py | 6 | Issue body extraction, JSON parsing, category/difficulty validation, injection |
| test_graph.py | 7 | Graph construction, node/edge presence, layout, missing slugs, colors |
| test_batch_import.py | 9 | Batch validation, mutual refs, duplicates, atomic rollback, directory load |
| **Total** | **70** (up from 18 at MVP) | |

### Tech Stack

| Layer | Choice |
|---|---|
| UI | Streamlit |
| Fuzzy search | rapidfuzz |
| Data validation | Pydantic v2 |
| Data format | JSON (one file per category) |
| Graph visualization | networkx + Plotly |
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
- Term relationship network graph (Plotly, collapsible expander)

### Features Implemented (Tooling & Automation)

- CLI term authoring tool with LLM-assisted generation (3 modes: interactive, manual, JSON import)
- Few-shot prompting with existing terms as style examples
- In-app suggestion form with input sanitization and rate limiting
- GitHub Action: label-triggered term generation → PR creation
- 3-layer input validation: sanitize at form → re-sanitize in Action → Pydantic validates before write
- Safe error logging with automatic API key redaction
- Batch import mode with atomic validation (--batch-dir, JSON array support)
- Branch protection on `main`

### Out of Scope (Documented for Future)

- Quiz/flashcard mode
- User progress tracking
- PDF export
- Admin interface for editing terms
- Authentication
