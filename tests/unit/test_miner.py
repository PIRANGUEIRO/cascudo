import networkx as nx
from cascudo_core.patterns.miner import mine_patterns


def test_miner_chain_3():
    g = nx.DiGraph()
    g.add_edge("a", "b", kind="CALLS")
    g.add_edge("b", "c", kind="CALLS")
    g.add_node("a", kind="function")
    g.add_node("b", kind="function")
    g.add_node("c", kind="function")
    pats = mine_patterns(g)
    assert len(pats) >= 1
    assert any(p.kind in ("chain_3", "trigram") for p in pats)
