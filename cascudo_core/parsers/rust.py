"""Parser Rust — stub escalável."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from . import Edge, ParseResult, Symbol, register

_RE_FN = re.compile(r"^\s*(?:pub\s+)?fn\s+(\w+)\s*\(", re.MULTILINE)
_RE_IMPORT = re.compile(r"^\s*use\s+([^;]+);", re.MULTILINE)


class RustParser:
    lang = "rust"
    extensions = (".rs",)

    def can_parse(self, path: Path) -> bool:
        return path.suffix == ".rs"

    def parse(self, path: Path, content: str) -> ParseResult:
        file_s = str(path)
        loc = content.count("\n") + 1
        h = hashlib.sha256(content.encode()).hexdigest()[:12]
        symbols: list[Symbol] = []
        edges: list[Edge] = []
        for m in _RE_FN.finditer(content):
            name = m.group(1)
            line = content[: m.start()].count("\n") + 1
            symbols.append(Symbol(kind="function", name=name, qualified_name=f"{path.stem}.{name}", file=file_s, line=line, col=0, is_entrypoint=name == "main", lang=self.lang))
        for m in _RE_IMPORT.finditer(content):
            target = m.group(1).strip()
            line = content[: m.start()].count("\n") + 1
            edges.append(Edge(kind="IMPORTS", source=file_s, target=target, file=file_s, line=line))
        return ParseResult(file=file_s, lang=self.lang, symbols=symbols, edges=edges, loc=loc, hash=h)


register(RustParser())  # type: ignore[arg-type]
