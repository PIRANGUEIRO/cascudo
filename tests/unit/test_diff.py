from pathlib import Path

from cascudo_core.diff import diff_graphs
from cascudo_core.graph.builder import build_graph
from cascudo_core.walker import walk_and_parse

FIXTURES = Path(__file__).parents[2] / "fixtures"


def test_diff():
    r1 = walk_and_parse(FIXTURES / "js-todo")
    r2 = walk_and_parse(FIXTURES / "go-todo")
    g1 = build_graph(r1).graph
    g2 = build_graph(r2).graph
    d = diff_graphs(g1, g2)
    assert "added" in d["nodes"]
    assert d["summary"].startswith("+")
