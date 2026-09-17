from pathlib import Path
from cascudo_core.walker import walk_and_parse
from cascudo_core.graph.builder import build_graph
from cascudo_core.analyzers import find_dead, find_cycles


def test_js_todo_pipeline():
    root = Path(__file__).parent.parent.parent / "fixtures" / "js-todo"
    results = walk_and_parse(root)
    assert len(results) >= 5
    bundle = build_graph(results)
    g = bundle.graph
    assert g.number_of_nodes() > 10
    dead = find_dead(g)
    # old.js tem dead
    assert any("old" in d["file"] for d in dead)
    cycles = find_cycles(g)
    # app.js <-> routes.js ciclo
    assert len(cycles) >= 1
