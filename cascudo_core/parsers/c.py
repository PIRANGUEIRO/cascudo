"""Parser C/C++ — stub escalável."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from . import Edge, ParseResult, Symbol, register

_RE_FUNC = re.compile(r"^\s*(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*\{", re.MULTILINE)
_RE_INCLUDE = re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]', re.MULTILINE)


class CParser:
    lang = "c"
    extensions = (".c", ".cpp", ".h", ".hpp", ".cc")

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    def parse(self, path: Path, content: str) -> ParseResult:
        file_s = str(path)
        loc = content.count("\n") + 1
        h = hashlib.sha256(content.encode()).hexdigest()[:12]
        symbols: list[Symbol] = []
        edges: list[Edge] = []
        for m in _RE_FUNC.finditer(content):
            name = m.group(1)
            if name in ("if", "for", "while", "return", "sizeof"):
                continue
            line = content[: m.start()].count("\n") + 1
            symbols.append(Symbol(kind="function", name=name, qualified_name=f"{path.stem}.{name}", file=file_s, line=line, col=0, lang=self.lang))
        for m in _RE_INCLUDE.finditer(content):
            target = m.group(1)
            line = content[: m.start()].count("\n") + 1
            edges.append(Edge(kind="IMPORTS", source=file_s, target=target, file=file_s, line=line))
        return ParseResult(file=file_s, lang=self.lang, symbols=symbols, edges=edges, loc=loc, hash=h)


register(CParser())  # type: ignore[arg-type]
