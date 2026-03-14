"""Fuzzy search and browse logic using rapidfuzz."""

from rapidfuzz import process

from core.models import Term

MIN_MATCH_SCORE: int = 60


def _build_choices(
    terms: dict[str, Term],
    category_filter: str | None = None,
) -> dict[str, str]:
    """Build a {slug: searchable_string} mapping for rapidfuzz.

    Args:
        terms: Full terms_by_slug dictionary.
        category_filter: If set, only include terms in this category.

    Returns:
        Dict mapping slug to a searchable string of term name + tags.
    """
    choices: dict[str, str] = {}
    for slug, term in terms.items():
        if category_filter and term.category != category_filter:
            continue
        choices[slug] = f"{term.term} {' '.join(term.tags)}"
    return choices


def search_best_match(
    query: str,
    terms: dict[str, Term],
    category_filter: str | None = None,
) -> Term | None:
    """Return the single best fuzzy match for a query.

    Args:
        query: User search string.
        terms: Full terms_by_slug dictionary.
        category_filter: Optional category key to restrict search scope.

    Returns:
        The best matching Term, or None if no match exceeds MIN_MATCH_SCORE.
    """
    choices = _build_choices(terms, category_filter)
    if not choices:
        return None

    result = process.extractOne(
        query, choices, score_cutoff=MIN_MATCH_SCORE
    )
    if result is None:
        return None

    matched_slug = result[2]
    return terms[matched_slug]


def search_suggestions(
    query: str,
    terms: dict[str, Term],
    limit: int = 5,
    category_filter: str | None = None,
) -> list[Term]:
    """Return top fuzzy matches for autocomplete suggestions.

    Args:
        query: User search string.
        terms: Full terms_by_slug dictionary.
        limit: Maximum number of suggestions to return.
        category_filter: Optional category key to restrict search scope.

    Returns:
        List of matching Term objects, ordered by score descending.
    """
    choices = _build_choices(terms, category_filter)
    if not choices:
        return []

    results = process.extract(
        query, choices, limit=limit, score_cutoff=MIN_MATCH_SCORE
    )
    return [terms[r[2]] for r in results]


def get_available_letters(terms: list[Term]) -> list[str]:
    """Return sorted unique first letters from a list of terms.

    Args:
        terms: List of Term objects.

    Returns:
        Sorted list of uppercase first-letter strings.
    """
    letters = {t.term[0].upper() for t in terms if t.term}
    return sorted(letters)


def group_terms_by_letter(
    terms: list[Term],
) -> dict[str, list[Term]]:
    """Group terms by their first letter.

    Args:
        terms: List of Term objects.

    Returns:
        Dict mapping uppercase letter to sorted list of terms.
    """
    groups: dict[str, list[Term]] = {}
    for t in terms:
        if not t.term:
            continue
        letter = t.term[0].upper()
        groups.setdefault(letter, []).append(t)
    for letter in groups:
        groups[letter].sort(key=lambda t: t.term)
    return groups
