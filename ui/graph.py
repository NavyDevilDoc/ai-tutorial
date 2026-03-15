"""Term relationship graph visualization using Plotly."""

import plotly.graph_objects as go
import streamlit as st

from core.graph import build_term_graph, get_graph_layout, get_node_color
from core.models import Term


def render_term_graph(
    term: Term,
    terms_by_slug: dict[str, Term],
) -> None:
    """Render an interactive relationship graph for a term.

    Args:
        term: The currently selected term.
        terms_by_slug: Complete slug-to-Term mapping.
    """
    graph = build_term_graph(term, terms_by_slug)
    if len(graph.nodes) < 2:
        return

    with st.expander("Term Relationships", expanded=False):
        layout = get_graph_layout(graph)
        fig = _build_plotly_figure(graph, layout)
        st.plotly_chart(fig, width="stretch")


def _build_plotly_figure(
    graph,
    layout: dict[str, tuple[float, float]],
) -> go.Figure:
    """Convert a networkx graph + layout into a Plotly figure.

    Args:
        graph: The networkx Graph with node attributes.
        layout: Position dict from get_graph_layout.

    Returns:
        A Plotly Figure object.
    """
    edge_x, edge_y = _build_edge_traces(graph, layout)
    node_trace = _build_node_trace(graph, layout)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=edge_x, y=edge_y,
                mode="lines",
                line=dict(width=1, color="#888"),
                hoverinfo="none",
            ),
            node_trace,
        ],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=10, l=10, r=10, t=10),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=350,
        ),
    )
    return fig


def _build_edge_traces(
    graph,
    layout: dict[str, tuple[float, float]],
) -> tuple[list[float | None], list[float | None]]:
    """Build x/y coordinate lists for edges.

    Args:
        graph: The networkx Graph.
        layout: Position dict.

    Returns:
        Tuple of (edge_x, edge_y) lists with None separators.
    """
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for u, v in graph.edges():
        x0, y0 = layout[u]
        x1, y1 = layout[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    return edge_x, edge_y


def _build_node_trace(
    graph,
    layout: dict[str, tuple[float, float]],
) -> go.Scatter:
    """Build the node scatter trace with colors and labels.

    Args:
        graph: The networkx Graph with node attributes.
        layout: Position dict.

    Returns:
        A Plotly Scatter trace for nodes.
    """
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []

    for node in graph.nodes():
        x, y = layout[node]
        node_x.append(x)
        node_y.append(y)

        data = graph.nodes[node]
        name = data.get("name", node)
        difficulty = data.get("difficulty", "beginner")
        is_center = data.get("is_center", False)

        node_text.append(name)
        node_colors.append(get_node_color(difficulty))
        node_sizes.append(20 if is_center else 12)

    return go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        textfont=dict(size=10),
        hoverinfo="text",
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=1, color="#fff"),
        ),
    )
