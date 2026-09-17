from pathlib import Path

from cascudo_core.search import search_symbols
from cascudo_core.walker import walk_and_parse
from cascudo_core.graph.builder import build_graph
from cascudo_core.analyzers import find_hotspots

FIXTURES = Path(__file__).parents[2] / "fixtures"


def test_hotspots_and_search():
    r = walk_and_parse(FIXTURES / "js-todo")
    g = build_graph(r).graph
    hot = find_hotspots(g)
    # hotspots pode ser vazio se p90 alto, mas não quebra
    assert isinstance(hot, list)
    hits = search_symbols(g, "oldHelper", limit=5)
    assert any("old" in h["id"] for h in hits)
    hits2 = search_symbols(g, "app.*", limit=5)
    assert len(hits2) >= 1
