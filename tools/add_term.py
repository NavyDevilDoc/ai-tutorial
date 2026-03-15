#!/usr/bin/env python3
"""CLI tool for adding new terms to the AI Literacy Tutor glossary.

Supports two modes:
  Interactive:  uv run python tools/add_term.py
  Automated:    uv run python tools/add_term.py --term "Compute" --category ml_fundamentals --difficulty beginner

When ANTHROPIC_API_KEY is set, generates a full term entry using few-shot
prompting with existing terms as examples. Otherwise, prompts for manual input.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Add project root to path so core imports work
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.constants import CATEGORY_DISPLAY_NAMES
from core.loader import _load_all_terms_impl
from core.models import Term

DATA_DIR = PROJECT_ROOT / "data"
VALID_CATEGORIES = list(CATEGORY_DISPLAY_NAMES.keys())
VALID_DIFFICULTIES = ["beginner", "intermediate", "advanced"]


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------

def make_slug(term_name: str) -> str:
    """Convert a term name to a URL-safe slug.

    Args:
        term_name: Human-readable term name.

    Returns:
        Lowercase, hyphen-separated slug.
    """
    slug = term_name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


# ---------------------------------------------------------------------------
# LLM generation
# ---------------------------------------------------------------------------

def _get_few_shot_examples(category: str, count: int = 3) -> list[dict]:
    """Load a few existing terms from a category as examples.

    Args:
        category: Category file key.
        count: Number of examples to include.

    Returns:
        List of raw term dicts.
    """
    file_path = DATA_DIR / f"{category}.json"
    if not file_path.exists():
        return []
    terms = json.loads(file_path.read_text(encoding="utf-8"))
    return terms[:count]


def _build_prompt(
    term_name: str,
    slug: str,
    category: str,
    difficulty: str,
    examples: list[dict],
) -> str:
    """Build the few-shot prompt for term generation.

    Args:
        term_name: The new term to define.
        slug: Generated slug.
        category: Target category key.
        difficulty: Difficulty level.
        examples: Existing terms to use as style examples.

    Returns:
        Complete prompt string.
    """
    examples_text = json.dumps(examples, indent=2)

    return f"""You are writing entries for an AI/ML glossary designed for non-technical
business professionals. Each entry must be clear, accurate, and jargon-free.

Here are {len(examples)} existing entries from the "{category}" category to match in
tone, depth, and structure:

{examples_text}

Now write a new entry for the term "{term_name}" with these exact fields:

- term: "{term_name}"
- slug: "{slug}"
- category: "{category}"
- difficulty: "{difficulty}"
- definition: Plain English, 1-3 sentences. No jargon without explanation.
- analogy: A non-technical metaphor that makes the concept click. Start with "Like..."
- use_in_a_sentence: A realistic private-sector business scenario.
- business_context: Why this matters for business decisions. 1-2 sentences.
- related_terms: 3-5 slugs of related concepts (use lowercase-hyphen format).
  Only reference terms that likely exist in a broad AI/ML glossary.
- tags: 2-4 lowercase tags for searchability. Include the common acronym if one exists.

Return ONLY valid JSON — a single object, no markdown fences, no explanation."""


def generate_term_with_llm(
    term_name: str,
    slug: str,
    category: str,
    difficulty: str,
) -> dict | None:
    """Generate a term entry using the Anthropic API.

    Args:
        term_name: The new term to define.
        slug: Generated slug.
        category: Target category key.
        difficulty: Difficulty level.

    Returns:
        Generated term dict, or None if API unavailable.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        from anthropic import Anthropic
    except ImportError:
        print("Warning: anthropic package not installed. Run: uv add --dev anthropic")
        return None

    examples = _get_few_shot_examples(category)
    prompt = _build_prompt(term_name, slug, category, difficulty, examples)

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Manual input
# ---------------------------------------------------------------------------

def prompt_for_field(field_name: str, hint: str = "") -> str:
    """Prompt the user for a single text field.

    Args:
        field_name: Display name of the field.
        hint: Optional hint text.

    Returns:
        User-provided string.
    """
    label = f"  {field_name}"
    if hint:
        label += f" ({hint})"
    label += ": "
    value = input(label).strip()
    while not value:
        print(f"    {field_name} is required.")
        value = input(label).strip()
    return value


def prompt_for_list(field_name: str, hint: str = "") -> list[str]:
    """Prompt the user for a comma-separated list.

    Args:
        field_name: Display name of the field.
        hint: Optional hint text.

    Returns:
        List of trimmed strings.
    """
    label = f"  {field_name}"
    if hint:
        label += f" ({hint})"
    label += ": "
    raw = input(label).strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def build_term_manually(
    term_name: str,
    slug: str,
    category: str,
    difficulty: str,
) -> dict:
    """Interactively prompt for all term fields.

    Args:
        term_name: The term name.
        slug: Generated slug.
        category: Target category.
        difficulty: Difficulty level.

    Returns:
        Complete term dict.
    """
    print("\nEnter the following fields:")
    return {
        "term": term_name,
        "slug": slug,
        "category": category,
        "difficulty": difficulty,
        "definition": prompt_for_field("definition", "plain English, 1-3 sentences"),
        "analogy": prompt_for_field("analogy", "non-technical metaphor"),
        "use_in_a_sentence": prompt_for_field(
            "use_in_a_sentence", "realistic business scenario"
        ),
        "business_context": prompt_for_field(
            "business_context", "why it matters for business"
        ),
        "related_terms": prompt_for_list(
            "related_terms", "comma-separated slugs"
        ),
        "tags": prompt_for_list("tags", "comma-separated, lowercase"),
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_term(term_data: dict) -> tuple[bool, str]:
    """Validate a term dict against the schema and existing data.

    Args:
        term_data: The term dict to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    try:
        term = Term(**term_data)
    except Exception as exc:
        return False, f"Schema validation failed: {exc}"

    try:
        terms_by_slug, _ = _load_all_terms_impl()
    except Exception as exc:
        return False, f"Could not load existing terms: {exc}"

    if term.slug in terms_by_slug:
        return False, f"Slug '{term.slug}' already exists"

    all_slugs = set(terms_by_slug.keys()) | {term.slug}
    for ref in term.related_terms:
        if ref not in all_slugs:
            print(f"  Warning: related term '{ref}' not found in glossary")

    return True, ""


# ---------------------------------------------------------------------------
# File writing
# ---------------------------------------------------------------------------

def append_to_category(term_data: dict, category: str) -> Path:
    """Append a validated term to its category JSON file.

    Args:
        term_data: The validated term dict.
        category: Category file key.

    Returns:
        Path to the modified file.
    """
    file_path = DATA_DIR / f"{category}.json"
    if file_path.exists():
        terms = json.loads(file_path.read_text(encoding="utf-8"))
    else:
        terms = []

    terms.append(term_data)
    file_path.write_text(
        json.dumps(terms, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return file_path


# ---------------------------------------------------------------------------
# Interactive flow
# ---------------------------------------------------------------------------

def choose_from_list(prompt_text: str, options: list[str]) -> str:
    """Display numbered options and return the user's choice.

    Args:
        prompt_text: Header text to display.
        options: List of option strings.

    Returns:
        The selected option string.
    """
    print(f"\n{prompt_text}")
    for i, opt in enumerate(options, 1):
        display = CATEGORY_DISPLAY_NAMES.get(opt, opt)
        print(f"  {i}. {display}")

    while True:
        choice = input("  Choice: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(f"  Enter a number between 1 and {len(options)}")


def review_and_confirm(term_data: dict) -> str:
    """Display generated term and ask for approval.

    Args:
        term_data: The term dict to review.

    Returns:
        One of 'approve', 'edit', 'regenerate', 'cancel'.
    """
    print("\n" + "=" * 60)
    print("GENERATED TERM ENTRY")
    print("=" * 60)
    print(json.dumps(term_data, indent=2, ensure_ascii=False))
    print("=" * 60)

    print("\nOptions:")
    print("  [a] Approve and save")
    print("  [e] Edit fields manually")
    print("  [r] Regenerate with LLM")
    print("  [c] Cancel")

    while True:
        choice = input("  Choice: ").strip().lower()
        if choice in ("a", "e", "r", "c"):
            return {"a": "approve", "e": "edit", "r": "regenerate", "c": "cancel"}[
                choice
            ]
        print("  Enter a, e, r, or c")


def edit_term(term_data: dict) -> dict:
    """Let the user edit specific fields of a term.

    Args:
        term_data: The current term dict.

    Returns:
        Updated term dict.
    """
    editable = [
        "definition", "analogy", "use_in_a_sentence",
        "business_context", "related_terms", "tags",
    ]
    print("\nEditable fields:")
    for i, field in enumerate(editable, 1):
        print(f"  {i}. {field}")
    print("  0. Done editing")

    while True:
        choice = input("  Edit field #: ").strip()
        if choice == "0":
            break
        if choice.isdigit() and 1 <= int(choice) <= len(editable):
            field = editable[int(choice) - 1]
            if field in ("related_terms", "tags"):
                current = ", ".join(term_data[field])
                print(f"    Current: {current}")
                new_val = input(f"    New {field} (comma-separated): ").strip()
                term_data[field] = [
                    v.strip() for v in new_val.split(",") if v.strip()
                ]
            else:
                print(f"    Current: {term_data[field]}")
                new_val = input(f"    New {field}: ").strip()
                if new_val:
                    term_data[field] = new_val
        else:
            print(f"  Enter 0-{len(editable)}")

    return term_data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Add a new term to the AI Literacy Tutor glossary."
    )
    parser.add_argument("--term", help="Term name (e.g. 'Compute')")
    parser.add_argument(
        "--category",
        choices=VALID_CATEGORIES,
        help="Target category",
    )
    parser.add_argument(
        "--difficulty",
        choices=VALID_DIFFICULTIES,
        help="Difficulty level",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip LLM generation, enter all fields manually",
    )
    parser.add_argument(
        "--json-file",
        help="Path to a JSON file containing the term entry (bypasses prompts)",
    )
    return parser.parse_args()


def main() -> None:
    """Run the add-term CLI workflow."""
    args = parse_args()

    # Mode 1: Import from JSON file (for automation)
    if args.json_file:
        raw = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
        is_valid, error = validate_term(raw)
        if not is_valid:
            print(f"Validation failed: {error}")
            sys.exit(1)
        path = append_to_category(raw, raw["category"])
        print(f"Added '{raw['term']}' to {path}")
        return

    # Mode 2: Interactive
    term_name = args.term or input("\nTerm name: ").strip()
    if not term_name:
        print("Term name is required.")
        sys.exit(1)

    slug = make_slug(term_name)
    print(f"  Generated slug: {slug}")

    category = args.category or choose_from_list(
        "Select category:", VALID_CATEGORIES
    )
    difficulty = args.difficulty or choose_from_list(
        "Select difficulty:", VALID_DIFFICULTIES
    )

    # Try LLM generation
    term_data = None
    if not args.no_llm:
        print("\nGenerating with LLM...")
        term_data = generate_term_with_llm(term_name, slug, category, difficulty)
        if term_data is None:
            print("LLM unavailable (no ANTHROPIC_API_KEY or missing package).")
            print("Falling back to manual input.\n")

    # Review loop
    while True:
        if term_data is None:
            term_data = build_term_manually(term_name, slug, category, difficulty)

        decision = review_and_confirm(term_data)

        if decision == "approve":
            break
        elif decision == "edit":
            term_data = edit_term(term_data)
        elif decision == "regenerate":
            print("\nRegenerating...")
            term_data = generate_term_with_llm(
                term_name, slug, category, difficulty
            )
            if term_data is None:
                print("LLM unavailable. Returning to manual edit.")
                term_data = build_term_manually(
                    term_name, slug, category, difficulty
                )
        elif decision == "cancel":
            print("Cancelled.")
            sys.exit(0)

    # Validate
    is_valid, error = validate_term(term_data)
    if not is_valid:
        print(f"\nValidation failed: {error}")
        sys.exit(1)

    # Write
    path = append_to_category(term_data, category)
    print(f"\nAdded '{term_name}' to {path}")
    print(f"Permalink: ?term={slug}")

    # Show post-add stats
    terms = json.loads(path.read_text(encoding="utf-8"))
    print(f"Category now has {len(terms)} terms.")


if __name__ == "__main__":
    main()
