"""Parser Java — regex determinístico escalável."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from . import Edge, ParseResult, Symbol, register

_RE_CLASS = re.compile(r"^\s*(?:public\s+)?(?:class|interface|enum)\s+(\w+)", re.MULTILINE)
_RE_METHOD = re.compile(r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+)?\s*\{", re.MULTILINE)
_RE_IMPORT = re.compile(r"^\s*import\s+([^;]+);", re.MULTILINE)


class JavaParser:
    lang = "java"
    extensions = (".java",)

    def can_parse(self, path: Path) -> bool:
        return path.suffix == ".java"

    def parse(self, path: Path, content: str) -> ParseResult:
        file_s = str(path)
        loc = content.count("\n") + 1
        h = hashlib.sha256(content.encode()).hexdigest()[:12]
        symbols: list[Symbol] = []
        edges: list[Edge] = []
        for m in _RE_CLASS.finditer(content):
            name = m.group(1)
            line = content[: m.start()].count("\n") + 1
            symbols.append(Symbol(kind="class", name=name, qualified_name=f"{path.stem}.{name}", file=file_s, line=line, col=0, lang=self.lang))
        for m in _RE_METHOD.finditer(content):
            name = m.group(1)
            if name in ("if", "for", "while", "switch"):
                continue
            line = content[: m.start()].count("\n") + 1
            # evita duplicar class como method
            if any(s.name == name and s.kind == "class" for s in symbols):
                continue
            symbols.append(Symbol(kind="function", name=name, qualified_name=f"{path.stem}.{name}", file=file_s, line=line, col=0, cc=1, lang=self.lang))
        for m in _RE_IMPORT.finditer(content):
            target = m.group(1).strip()
            line = content[: m.start()].count("\n") + 1
            edges.append(Edge(kind="IMPORTS", source=file_s, target=target, file=file_s, line=line))
        return ParseResult(file=file_s, lang=self.lang, symbols=symbols, edges=edges, loc=loc, hash=h)


register(JavaParser())  # type: ignore[arg-type]
