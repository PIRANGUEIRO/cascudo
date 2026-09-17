from pathlib import Path
from cascudo_core.walker import walk_and_parse

def test_all_langs():
    for name in ["js-todo","go-todo","java-todo"]:
        r = walk_and_parse(Path(f"/home/binho/cascudo/fixtures/{name}"))
        assert len(r) >= 1
        assert any(len(x.symbols) > 0 for x in r), f"{name} sem símbolos"
