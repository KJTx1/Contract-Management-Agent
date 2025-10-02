"""Main graph export for LangGraph deployment."""

# Import the standalone graph that works with LangGraph Studio
try:
    # Try relative import first (when imported as package)
    from .standalone_graph import graph
except ImportError:
    # Fall back to absolute import (when loaded directly by LangGraph Studio)
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from standalone_graph import graph

__all__ = ["graph"]
