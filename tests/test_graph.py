"""Tests for term relationship graph construction."""

from core.graph import build_term_graph, get_graph_layout, get_node_color
from core.models import Term


def test_build_graph_has_center_node(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """The graph should contain the selected term as a node."""
    term = sample_terms_by_slug["alpha-term"]
    graph = build_term_graph(term, sample_terms_by_slug)
    assert "alpha-term" in graph.nodes
    assert graph.nodes["alpha-term"]["is_center"] is True


def test_build_graph_has_related_nodes(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """All valid related terms should appear as nodes."""
    term = sample_terms_by_slug["alpha-term"]
    graph = build_term_graph(term, sample_terms_by_slug)
    assert "beta-term" in graph.nodes
    assert graph.nodes["beta-term"]["is_center"] is False


def test_build_graph_has_edges(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """Edges should connect center to related terms."""
    term = sample_terms_by_slug["alpha-term"]
    graph = build_term_graph(term, sample_terms_by_slug)
    assert graph.has_edge("alpha-term", "beta-term")


def test_build_graph_skips_missing_slugs(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """Related terms not in the index should be silently skipped."""
    # gamma-term references delta-term which exists, but also has no
    # references to non-existent terms in our fixture
    term = Term(
        term="Test",
        slug="test-node",
        category="test",
        difficulty="beginner",
        definition="Test.",
        analogy="Test.",
        use_in_a_sentence="Test.",
        business_context="Test.",
        related_terms=["nonexistent-slug", "alpha-term"],
        tags=["test"],
    )
    graph = build_term_graph(term, sample_terms_by_slug)
    assert "nonexistent-slug" not in graph.nodes
    assert "alpha-term" in graph.nodes


def test_build_graph_empty_related() -> None:
    """A term with no related_terms should produce a single-node graph."""
    term = Term(
        term="Lonely",
        slug="lonely",
        category="test",
        difficulty="beginner",
        definition="No friends.",
        analogy="Like being alone.",
        use_in_a_sentence="Lonely term.",
        business_context="Isolation.",
        related_terms=[],
        tags=["test"],
    )
    graph = build_term_graph(term, {})
    assert len(graph.nodes) == 1
    assert "lonely" in graph.nodes


def test_get_graph_layout_returns_positions(
    sample_terms_by_slug: dict[str, Term],
) -> None:
    """Layout should return a position for every node."""
    term = sample_terms_by_slug["alpha-term"]
    graph = build_term_graph(term, sample_terms_by_slug)
    layout = get_graph_layout(graph)
    for node in graph.nodes:
        assert node in layout
        x, y = layout[node]
        assert isinstance(x, float)
        assert isinstance(y, float)


def test_get_node_color_values() -> None:
    """Each difficulty should map to a hex color."""
    assert get_node_color("beginner").startswith("#")
    assert get_node_color("intermediate").startswith("#")
    assert get_node_color("advanced").startswith("#")
    assert get_node_color("unknown").startswith("#")
