"""Pure-logic helpers for term navigation history."""

from core.constants import MAX_HISTORY_DEPTH


def push_term_history(
    history: list[str],
    slug: str,
    max_depth: int = MAX_HISTORY_DEPTH,
) -> list[str]:
    """Add a slug to the history stack, capping at max_depth.

    Args:
        history: Current history list (most recent at end).
        slug: The slug to push.
        max_depth: Maximum stack size.

    Returns:
        Updated history list.
    """
    if not slug:
        return history
    history = history + [slug]
    if len(history) > max_depth:
        history = history[-max_depth:]
    return history


def pop_term_history(
    history: list[str],
) -> tuple[str | None, list[str]]:
    """Pop the most recent slug from the history stack.

    Args:
        history: Current history list.

    Returns:
        Tuple of (popped slug or None, remaining history).
    """
    if not history:
        return None, history
    return history[-1], history[:-1]
