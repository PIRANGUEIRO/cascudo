"""Parser Python — stub escalável (mesma interface)."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from . import Edge, ParseResult, Symbol, register

_RE_FUNC = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(|^\s*class\s+(\w+)", re.MULTILINE)
_RE_IMPORT = re.compile(r"^\s*(?:import|from)\s+(\w+)", re.MULTILINE)


class PyParser:
    lang = "python"
    extensions = (".py",)

    def can_parse(self, path: Path) -> bool:
        return path.suffix == ".py"

    def parse(self, path: Path, content: str) -> ParseResult:
        file_s = str(path)
        loc = content.count("\n") + 1
        h = hashlib.sha256(content.encode()).hexdigest()[:12]
        symbols: list[Symbol] = []
        edges: list[Edge] = []

        for m in _RE_FUNC.finditer(content):
            name = next(g for g in m.groups() if g)
            line = content[: m.start()].count("\n") + 1
            symbols.append(
                Symbol(
                    kind="function",
                    name=name,
                    qualified_name=f"{path.stem}.{name}",
                    file=file_s,
                    line=line,
                    col=0,
                    cc=1,
                    lang=self.lang,
                )
            )
        for m in _RE_IMPORT.finditer(content):
            target = m.group(1)
            line = content[: m.start()].count("\n") + 1
            edges.append(Edge(kind="IMPORTS", source=file_s, target=target, file=file_s, line=line))

        return ParseResult(file=file_s, lang=self.lang, symbols=symbols, edges=edges, loc=loc, hash=h)


register(PyParser())  # type: ignore[arg-type]
