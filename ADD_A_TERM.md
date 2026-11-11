# How to Add a Term

There are three ways to add terms to the AI Literacy Tutor glossary, depending on your role and access level.

---

## Method 1: Suggest via the App (Anyone)

Best for: end users, subject matter experts, anyone with a browser.

1. Go to the live app and scroll to **"Suggest a New Term"** at the bottom of the welcome page
2. Fill in the form:
   - **Term** (required) — the term as you'd hear it in a meeting
   - **Category** (required) — pick the closest match from the dropdown
   - **Difficulty** (required) — beginner (what it is), intermediate (how it works), advanced (deep technical)
   - **Definition / Analogy / Use in a Sentence / Business Context** (all optional) — fill in what you know; leave blank what you don't
   - **Note to maintainer** (optional) — where you heard the term, anything we should know
3. Click **Submit Suggestion**
4. A GitHub Issue is automatically created with the `term-suggestion` label

**What happens next:** A maintainer reviews the issue. If approved, they add the `term-approved` label, which triggers an automated pipeline. The pipeline calls Claude to generate a full glossary entry; **any prose fields you provided override the LLM's output** (user words always win, Claude backfills the blanks). The result is validated, opened as a Pull Request, reviewed, and merged. Railway auto-deploys.

**Rate limit:** Three suggestions per hour per IP.

---

## Method 2: Approve a Suggestion (Maintainer)

Best for: project maintainers reviewing user suggestions.

1. Go to [GitHub Issues](https://github.com/NavyDevilDoc/ai-tutorial/issues) and find issues labeled `term-suggestion`
2. Review the suggestion — is this a real term? Does it fit the glossary's audience?
3. If approved, add the **`term-approved`** label (blue) to the issue
   - Click the gear icon next to Labels in the issue sidebar
   - Search for `term-approved` and check it
   - Click outside the dropdown to apply
4. A GitHub Action automatically:
   - Extracts the term data from the issue (including any prose fields the user provided)
   - Calls Claude to generate the full 10-field glossary entry using few-shot prompting
   - Overlays user-provided `definition` / `analogy` / `use_in_a_sentence` / `business_context` on top of the LLM output (user wins)
   - Validates the entry with Pydantic (schema, slug format, uniqueness)
   - Strips any dangling `related_terms` references
   - Creates a branch and opens a Pull Request
   - Comments on the issue with a link to the PR
5. Review the PR — check that the definition is accurate, the analogy makes sense, and related terms are appropriate
6. Merge the PR — Railway auto-deploys within minutes

**If the Action fails:** Check the Actions tab for error logs. Common issues:
- `ANTHROPIC_API_KEY` not set as a GitHub secret
- Stale branch from a previous failed run (delete it and re-trigger by toggling the label)
- Slug already exists (the term is already in the glossary)

---

## Method 3: CLI Tool (Developer)

Best for: batch additions, local development, direct control.

### Prerequisites

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-your-key-here
# Or on Windows:
export $(cat .env | xargs)
```

### Interactive mode (LLM-assisted)

```bash
uv run python tools/add_term.py
```

You provide 3 inputs (term name, category, difficulty). Claude generates the rest. You review, edit, or regenerate before saving.

### Interactive mode (manual)

```bash
uv run python tools/add_term.py --no-llm
```

Prompts for all 10 fields manually. No API key needed.

### With arguments (for scripting)

```bash
uv run python tools/add_term.py --term "Compute" --category ml_fundamentals --difficulty beginner
```

### JSON file import (for automation)

```bash
uv run python tools/add_term.py --json-file path/to/term.json
```

The JSON file must contain a complete term object matching the Zod schema in `web/src/models.ts` (`TermSchema`).

### After adding terms locally

```bash
# Verify
uv run pytest tests/ -v

# Commit and push (via PR if branch protection is on)
git checkout -b add/new-terms
git add web/src/data/
git commit -m "Add new terms"
git push -u origin add/new-terms
gh pr create --title "Add new terms" --body "Description of terms added"
```

---

## Term Schema Reference

Every term must have these 10 fields:

| Field | Type | Rules |
|---|---|---|
| `term` | string | Display name as used in conversation |
| `slug` | string | Lowercase, hyphen-separated, globally unique |
| `category` | string | Must match a filename stem in `web/src/data/` (e.g., `ml_fundamentals`) |
| `difficulty` | string | One of: `beginner`, `intermediate`, `advanced` |
| `definition` | string | Plain English, 1-3 sentences, no unexplained jargon |
| `analogy` | string | Non-technical metaphor that makes the concept click |
| `use_in_a_sentence` | string | Realistic private-sector business scenario |
| `business_context` | string | Why this matters for business decisions |
| `related_terms` | list | Slugs of related terms (must exist in the glossary) |
| `tags` | list | Lowercase search tags; include common acronyms (e.g., `RAG`, `LLM`) |

## Valid Categories

| Key | Display Name |
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
