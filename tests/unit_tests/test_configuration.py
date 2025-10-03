from langgraph.pregel import Pregel

from agent.graph import graph


def test_graph_initialization() -> None:
    """Test that the graph is properly initialized."""
    assert isinstance(graph, Pregel)
