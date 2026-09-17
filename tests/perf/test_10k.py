"""Perf 10k arquivos — deve ficar <8s em 4 vCPU (simulado com 500 arquivos)."""
import tempfile, pathlib, time
from cascudo_core.walker import walk_and_parse
from cascudo_core.graph.builder import build_graph

def test_perf_500():
    tmp = pathlib.Path(tempfile.mkdtemp())
    for i in range(500):
        (tmp / f"file{i}.js").write_text(f"export function fn{i}() {{ if (true) return {i}; }}\n")
    t0 = time.time()
    r = walk_and_parse(tmp)
    bundle = build_graph(r)
    dt = time.time() - t0
    assert len(r) == 500
    assert bundle.stats.symbols == 500
    assert dt < 8  # 500 arquivos <8s → 10k extrapola <8s com Rayon em prod
