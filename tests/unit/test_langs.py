from pathlib import Path

from cascudo_core.walker import walk_and_parse

FIXTURES = Path(__file__).parents[2] / "fixtures"


def test_all_langs():
    for name in ["js-todo", "go-todo", "java-todo"]:
        r = walk_and_parse(FIXTURES / name)
        assert len(r) >= 1
        assert any(len(x.symbols) > 0 for x in r), f"{name} sem símbolos"
