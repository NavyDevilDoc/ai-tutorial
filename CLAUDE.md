# CLAUDE.md — AI Literacy Tutor

## Project Purpose

A React-based AI literacy tool for non-technical professionals in the private sector. It presents a curated dictionary of AI/ML terms with plain-language definitions, real-world examples, and "use in a sentence" guidance. The goal is confident comprehension, not technical mastery.

A thin Node (Hono) server fronts the SPA with one API route — `POST /api/suggest` — which turns in-app term suggestions into GitHub Issues. A separate GitHub Action picks those issues up, uses Claude to flesh out any fields the suggester left blank, and opens a Pull Request.

---

## What This Project Is NOT

Do not over-engineer. This project intentionally excludes:
- LLM-generated or dynamic definitions in the live app (all served content is static and human-reviewed before merge)
- User authentication or accounts
- A database (all data lives in flat JSON files)
- An admin UI for editing terms
- Any infrastructure beyond Railway (single service, single Node process)

If a new feature seems to require any of the above, flag it for discussion rather than implementing it.

---

## Tech Stack

### Live app (served by Railway)

| Layer | Choice | Notes |
|---|---|---|
| Build + dev server | Vite 8 | React plugin, TypeScript, HMR |
| UI | React 18 + TypeScript | Function components, hooks |
| Styling | Tailwind 3 | HSL CSS variables for dark/light theme |
| Primitives | shadcn-style, hand-written | Copied into `web/src/components/ui/`, not a runtime UI library |
| Validation | Zod 4 | Single `TermSchema` used by loader + prebuild gate; single `SuggestionSchema` shared by RHF client + Hono server |
| Fuzzy search | Fuse.js 7 | Replaces rapidfuzz; score threshold 0.4 |
| Routing | React Router 7 | `BrowserRouter`; permalink support (`/term/:slug`) |
| Session state | Zustand 5 | Only the navigation history stack |
| Forms | React Hook Form 7 + `@hookform/resolvers` | Paired with shadcn `<Form>` + Zod |
| Graph viz | React Flow (`@xyflow/react`) 12 | Replaces networkx+Plotly |
| Server | Hono 4 + `@hono/node-server` | Single `server/index.ts`, serves `dist/` + `/api/*` |
| Testing | Vitest 5 + Testing Library + jsdom | 82 tests; `server/__tests__/*` + `src/__tests__/*` |
| Runtime | Node >=22 | Pinned via `engines` in `web/package.json`; Railway's Railpack detects it |
| Deploy | Railway | Root Directory = `web`; `web/Procfile` → `npm start` → `tsx server/index.ts` |

### Term-authoring pipeline (runs on GitHub)

| Layer | Choice | Notes |
|---|---|---|
| Content validator | Pydantic v2 | `core/models.py` — mirrors the Zod `TermSchema` |
| Data loading / validation | `core/data_loading.py` | Streamlit-free; used by CLI + Action |
| Input sanitization | `core/sanitize.py` | HTML stripping, control-char filtering, slug/term-name normalization |
| CLI tool | `tools/add_term.py` | LLM-assisted (default), manual, JSON import, and batch-dir modes |
| GitHub Action | `.github/workflows/term-from-issue.yml` + `.github/scripts/process_approved_term.py` | Triggers on `term-approved` label; writes directly to `web/src/data/<category>.json` and opens a PR |
| LLM | Anthropic Claude | `tools/add_term.py:generate_term_with_llm`; few-shot prompted with existing terms |
| Python runtime | 3.12+ | Managed with `uv` |

The pipeline and the live app share no runtime dependency — both read/write `web/src/data/*.json`, but neither imports the other at runtime.

---

## Project Structure

```
ai-tutorial/
├── CLAUDE.md                              ← this file
├── README.md
├── ADD_A_TERM.md                          ← three ways to add a term
├── PROGRESS.md                            ← historical development log (Streamlit era + migration)
├── LICENSE
├── pyproject.toml                         ← Python deps (pydantic only; anthropic + pytest as dev)
├── uv.lock
│
├── web/                                   ← the live app
│   ├── Procfile                           ← web: npm start
│   ├── package.json                       ← engines pin; tsx in deps so prod can run it
│   ├── tsconfig.json
│   ├── vite.config.ts                     ← /api/* proxy to :3000 in dev; Vitest config
│   ├── tailwind.config.ts
│   ├── index.html
│   ├── scripts/
│   │   └── validate-data.ts               ← prebuild gate: Zod-validates every JSON file
│   ├── server/
│   │   ├── index.ts                       ← Hono app: /api, /healthz, static dist/
│   │   ├── suggest.ts                     ← POST /api/suggest router factory
│   │   ├── github.ts                      ← fetch wrapper for GitHub Issues API
│   │   ├── rateLimit.ts                   ← in-memory per-IP, 3/hour
│   │   └── __tests__/                     ← github + suggest tests (Hono app.request)
│   └── src/
│       ├── main.tsx
│       ├── App.tsx                        ← BrowserRouter + route table
│       ├── index.css                      ← Tailwind directives + HSL theme variables
│       ├── constants.ts                   ← Display strings, difficulty colors, category display names
│       ├── models.ts                      ← Zod TermSchema + SuggestionSchema (shared with server)
│       ├── data/
│       │   ├── *.json                     ← the 137 production terms (SOURCE OF TRUTH)
│       │   ├── loader.ts                  ← pure loadFromRawCategories + compute helpers
│       │   └── index.ts                   ← Vite-only wrapper that globs *.json + caches
│       ├── lib/
│       │   ├── search.ts                  ← Fuse.js wrapper + letter helpers
│       │   ├── sanitize.ts                ← sanitizeText / sanitizeTermName / buildIssueBody
│       │   ├── history.ts                 ← pure push/pop stack helpers
│       │   ├── useFilters.ts              ← URL-synced filter state
│       │   ├── useTermNav.ts              ← goToTerm/goBack/goHome (centralizes history push)
│       │   ├── useTheme.ts                ← light/dark with localStorage + prefers-color-scheme
│       │   └── utils.ts                   ← cn() = tailwind-merge(clsx)
│       ├── state/
│       │   └── store.ts                   ← Zustand: history stack
│       ├── components/
│       │   ├── Layout.tsx                 ← header + sidebar + main outlet
│       │   ├── Sidebar.tsx                ← search + category + difficulty + letter + browse + reset
│       │   ├── TermCard.tsx               ← full term detail view
│       │   ├── RelatedPanel.tsx           ← clickable related-term cards
│       │   ├── TermGraph.tsx              ← React Flow relationship graph (collapsible)
│       │   ├── NavButtons.tsx             ← Home + Back
│       │   ├── SuggestionForm.tsx         ← RHF + shared SuggestionSchema
│       │   ├── ThemeToggle.tsx
│       │   └── ui/                        ← button, input, select, label, textarea, form
│       ├── routes/
│       │   ├── WelcomeRoute.tsx           ← hero + quick-starts + suggestion form + legacy ?term= redirect
│       │   └── TermRoute.tsx              ← composes NavButtons / TermCard / RelatedPanel / TermGraph
│       └── __tests__/                     ← Zod models, loader, search, history, sanitize, useFilters, TermCard, suggestionSchema
│
├── core/                                  ← Python shared libs for the authoring pipeline
│   ├── __init__.py
│   ├── constants.py                       ← CATEGORY_DISPLAY_NAMES (shared with Action)
│   ├── models.py                          ← Pydantic Term + validate_related_terms
│   ├── data_loading.py                    ← Pure load/validate; reads from web/src/data/
│   └── sanitize.py                        ← sanitize_term_name, sanitize_text
│
├── tools/
│   └── add_term.py                        ← CLI: interactive LLM / manual / --json-file / --batch-dir
│
├── .github/
│   ├── workflows/
│   │   └── term-from-issue.yml            ← label-triggered; writes to web/src/data/ + opens PR
│   └── scripts/
│       └── process_approved_term.py       ← extracts issue JSON + overlays user prose on LLM output
│
└── tests/                                 ← pytest; 47 tests for core/, tools/, and the Action
    ├── conftest.py
    ├── fixtures/
    ├── test_models.py
    ├── test_loader.py
    ├── test_sanitize.py
    ├── test_batch_import.py
    └── test_process_approved_term.py
```

**Rule:** `web/src/App.tsx` stays thin — only routing + layout. Features live in `components/` and `routes/`. Pure logic lives in `lib/`.

---

## Data Schema

Every term in `web/src/data/*.json` must satisfy `TermSchema` in `web/src/models.ts` (and the mirror Pydantic `Term` in `core/models.py` for the Action):

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
- `slug`: lowercase, hyphen-separated, globally unique (enforced by Zod regex + Pydantic validator)
- `difficulty`: one of `"beginner"`, `"intermediate"`, `"advanced"` (Zod enum / Pydantic Literal)
- `related_terms`: references slugs (not display names); cross-checked at load time
- `definition`: plain English, no jargon without a link to another term
- `analogy`: required — non-technical reference
- `use_in_a_sentence`: realistic private-sector business scenario

---

## Shared SuggestionSchema

`web/src/models.ts` also exports `SuggestionSchema`, the single source of truth for the suggestion form payload. Used by:
- `web/src/components/SuggestionForm.tsx` via `zodResolver` (client validation + inline errors)
- `web/server/suggest.ts` via `safeParse` (server validation before sanitize → GitHub)

Three required fields (`termName`, `category`, `difficulty`) + five optional prose fields (`definition`, `analogy`, `use_in_a_sentence`, `business_context`, `context`). Empty-string optionals normalize to `undefined` via Zod `.transform`.

---

## Core Logic (web/)

### `src/data/loader.ts`

- Pure `loadFromRawCategories(dict)` — validates every term with `TermSchema`, enforces slug uniqueness, cross-checks `related_terms`.
- Used by both the Vite runtime wrapper (`src/data/index.ts`) and the prebuild gate (`scripts/validate-data.ts`).

### `src/lib/search.ts`

- `searchBestMatch` / `searchSuggestions` via Fuse.js over `"${term.term} ${tags.join(' ')}"`.
- `SEARCH_THRESHOLD = 0.4` (inverted from rapidfuzz's 60-of-100; return `null` when no match beats it).
- `getAvailableLetters` / `groupTermsByLetter` for the sidebar letter row.

### `src/lib/useFilters.ts`

- Reads/writes filter state to URL search params (`?category=nlp&difficulty=beginner&letter=A&q=...`).
- `filterTerms(terms, filters)` is a pure helper tested in isolation.

### `src/lib/useTermNav.ts`

- `goToTerm(slug)` pushes the current term onto the history stack before navigating. `goBack` only pops. `goHome` clears.
- All forward term-navigation callsites use this hook — Sidebar search/browse, RelatedPanel links, TermGraph node clicks. Do NOT add a reactive history push in a `useEffect`; it causes oscillation on Back.

### `server/suggest.ts`

- Rate-limited (`createRateLimiter`, default 3/hour per IP).
- Validates with `SuggestionSchema.safeParse`, sanitizes each field, builds the issue body, posts via `server/github.ts`.

---

## UI Behavior

### Sidebar (`components/Sidebar.tsx`)
1. Text search with top-5 live suggestions (`searchSuggestions`); Enter picks the top match.
2. Category `<Select>` with per-category counts.
3. Difficulty row of button chips with counts that cascade from category.
4. Letter row of button chips (only letters that exist in the current filter set).
5. Browse `<Select>` listing the filtered terms.
6. "Reset Filters" clears all URL params.

### Term Card (`components/TermCard.tsx`)
In order: title, color-coded difficulty badge, category caption, definition, info callout (💡 Analogy), success callout (💼 Use in a Sentence), business context, tag chips.

### Related Terms (`components/RelatedPanel.tsx`)
Up to 6 related terms as clickable cards with one-line definitions. Click goes through `goToTerm` so history accumulates.

### Term Graph (`components/TermGraph.tsx`)
Collapsible React Flow radial layout. Center term + related terms color-coded by difficulty. Click a neighbor to navigate.

### Suggestion Form (`components/SuggestionForm.tsx`)
RHF + shared `SuggestionSchema`. Required: term + category + difficulty. Optional: definition / analogy / sentence / business context / note-to-maintainer. Submit → `POST /api/suggest` → GitHub Issue. User-provided prose fields win over the LLM during Action-time generation.

---

## URL / Session State

| Where | What |
|---|---|
| URL path (`/term/:slug`) | Which term is being viewed |
| URL search params (`?category=&difficulty=&letter=&q=`) | Filters |
| Zustand (`state/store.ts`) | Navigation history stack |
| `localStorage` (`useTheme`) | Light/dark preference |

No other session state. If you're about to add more, think twice — most things belong in the URL for shareability.

---

## Coding Conventions

- **TypeScript strict mode** — no implicit any; `noUnusedLocals`/`noUnusedParameters` on.
- **Type hints everywhere in Python** — no untyped signatures.
- **Docstrings on public functions** — one-line summary + Args/Returns.
- **No global mutable state** outside Zustand / `localStorage`.
- **No hardcoded display strings in components** — add to `src/constants.ts`.
- **Error handling:** 4xx on bad input, 429 on rate limit, 502 on upstream (GitHub) failure. Never leak tokens in error strings.
- **Function length cap: 40 lines** — split if longer.
- **File paths:** `pathlib.Path` in Python, `node:path` in TS. Never string concatenation.

---

## Categories

Nine category files live under `web/src/data/`:

| File key | Display name |
|---|---|
| `ml_fundamentals` | ML Fundamentals |
| `neural_networks` | Neural Networks |
| `nlp` | Natural Language Processing |
| `computer_vision` | Computer Vision |
| `mlops` | MLOps & Deployment |
| `statistics` | Statistics & Math |
| `generative_ai` | Generative AI |
| `ai_ethics` | AI Ethics & Governance |
| `business_strategy` | Business & Strategy |

Display names are in `src/constants.ts` (TS) and `core/constants.py` (Python).

---

## Running Locally

```bash
cd web
npm install
npm run dev     # concurrently: Vite on :5174, Hono on :3000, /api/* proxied
```

Prod shape (what Railway runs):

```bash
cd web
npm run build   # validate:data → tsc -b → vite build → dist/
npm start       # tsx server/index.ts → serves dist/ + /api/*
```

For the authoring pipeline:

```bash
uv sync                           # install pydantic + dev deps
uv run pytest tests/ -v           # 47 tests
uv run python tools/add_term.py   # add a term
```

---

## Testing

- Web: `npm --prefix web test` → Vitest (82 tests across 10 files, jsdom env)
- Python: `uv run pytest tests/ -v` → pytest (47 tests)
- Data: `npm --prefix web run validate:data` runs as part of `npm run build` — bad JSON fails CI before any build artifact is produced

Do not add mocks for the data loader; use fixture JSON or the `data_dir` parameter on `load_all_terms_impl`.

---

## Deployment

Railway service points at **Root Directory `web`**. Build is auto-detected by Railpack from `web/package.json` (`engines.node >=22`). Start is read from `web/Procfile` (`npm start`).

Environment variables on the Railway service:
- `GITHUB_TOKEN` — fine-grained PAT with Issues R/W on `NavyDevilDoc/ai-tutorial`
- Optional overrides: `GITHUB_REPO_OWNER` (default `NavyDevilDoc`), `GITHUB_REPO_NAME` (default `ai-tutorial`), `PORT` (default `3000`; Railway injects its own)

---

## Out of Scope (Do Not Implement)

- Quiz/flashcard mode
- User progress tracking
- PDF export
- Admin interface for editing terms
- Any LLM API calls from the live web app (LLM only runs inside the GitHub Action)
- Login or access control
