"""Graph construction for term relationship visualization."""

import networkx as nx

from core.constants import DIFFICULTY_COLORS
from core.models import Term


def build_term_graph(
    term: Term,
    terms_by_slug: dict[str, Term],
) -> nx.Graph:
    """Build a network graph centered on a term and its related terms.

    Args:
        term: The center term.
        terms_by_slug: Complete slug-to-Term mapping.

    Returns:
        A networkx Graph with node attributes: name, difficulty, is_center.
    """
    graph = nx.Graph()

    graph.add_node(
        term.slug,
        name=term.term,
        difficulty=term.difficulty,
        is_center=True,
    )

    for slug in term.related_terms:
        related = terms_by_slug.get(slug)
        if related is None:
            continue
        graph.add_node(
            slug,
            name=related.term,
            difficulty=related.difficulty,
            is_center=False,
        )
        graph.add_edge(term.slug, slug)

    return graph


def get_graph_layout(graph: nx.Graph) -> dict[str, tuple[float, float]]:
    """Compute a spring layout for the graph.

    Args:
        graph: A networkx Graph.

    Returns:
        Dict mapping node slug to (x, y) position tuple.
    """
    if len(graph.nodes) == 0:
        return {}
    if len(graph.nodes) == 1:
        node = list(graph.nodes)[0]
        return {node: (0.0, 0.0)}
    return nx.spring_layout(graph, seed=42)


def get_node_color(difficulty: str) -> str:
    """Map a difficulty level to a hex color for Plotly.

    Args:
        difficulty: One of 'beginner', 'intermediate', 'advanced'.

    Returns:
        Hex color string.
    """
    color_map = {
        "beginner": "#2ca02c",
        "intermediate": "#ff7f0e",
        "advanced": "#d62728",
    }
    return color_map.get(difficulty, "#999999")
