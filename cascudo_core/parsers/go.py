"""Parser Go — regex determinístico, interface escalável."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from . import Edge, ParseResult, Symbol, register

_RE_FUNC = re.compile(r"^\s*func\s+(?:\(\w+\s+[\*\w]+\s*\)\s*)?(\w+)\s*\(", re.MULTILINE)
_RE_IMPORT = re.compile(r'^\s*import\s+(?:\(\s*)?["`]([^"`]+)["`]', re.MULTILINE)
_RE_STRUCT = re.compile(r"^\s*type\s+(\w+)\s+struct", re.MULTILINE)


class GoParser:
    lang = "go"
    extensions = (".go",)

    def can_parse(self, path: Path) -> bool:
        return path.suffix == ".go"

    def parse(self, path: Path, content: str) -> ParseResult:
        file_s = str(path)
        loc = content.count("\n") + 1
        h = hashlib.sha256(content.encode()).hexdigest()[:12]
        symbols: list[Symbol] = []
        edges: list[Edge] = []

        for m in _RE_FUNC.finditer(content):
            name = m.group(1)
            line = content[: m.start()].count("\n") + 1
            symbols.append(
                Symbol(
                    kind="function",
                    name=name,
                    qualified_name=f"{path.stem}.{name}",
                    file=file_s,
                    line=line,
                    col=0,
                    cc=content[m.start() : m.start() + 800].count("if ") + 1,
                    is_entrypoint=name == "main" and path.name == "main.go",
                    lang=self.lang,
                )
            )
        for m in _RE_STRUCT.finditer(content):
            name = m.group(1)
            line = content[: m.start()].count("\n") + 1
            symbols.append(
                Symbol(kind="class", name=name, qualified_name=f"{path.stem}.{name}", file=file_s, line=line, col=0, lang=self.lang)
            )
        for m in _RE_IMPORT.finditer(content):
            target = m.group(1)
            line = content[: m.start()].count("\n") + 1
            edges.append(Edge(kind="IMPORTS", source=file_s, target=target, file=file_s, line=line))

        # CALLS intra-file (mesma lógica JS, corpo entre {})
        _RE_CALL = re.compile(r"(\w+)\s*\(")

        def _body(start: int) -> str:
            i = content.find("{", start)
            if i == -1:
                return content[start : start + 600]
            depth = 0
            for j in range(i, min(len(content), i + 1500)):
                if content[j] == "{":
                    depth += 1
                elif content[j] == "}":
                    depth -= 1
                    if depth == 0:
                        return content[i : j + 1]
            return content[i : i + 800]

        func_names = {s.name for s in symbols}
        snippets = {}
        for m, s in zip(_RE_FUNC.finditer(content), [s for s in symbols if s.kind == "function"]):
            snippets[s.qualified_name] = _body(m.start())
        for s in symbols:
            if s.kind != "function":
                continue
            body = snippets.get(s.qualified_name, "")
            body_no_def = re.sub(r"func\s+\w+\s*\(", "", body)
            for cm in _RE_CALL.finditer(body_no_def):
                callee = cm.group(1)
                if callee in func_names and callee != s.name and callee not in ("if", "for", "switch", "Println", "Printf"):
                    before = body_no_def[max(0, cm.start() - 12) : cm.start()]
                    if "func" in before:
                        continue
                    edges.append(Edge(kind="CALLS", source=s.qualified_name, target=f"{Path(file_s).stem}.{callee}", file=file_s, line=s.line, confidence="medium"))

        return ParseResult(file=file_s, lang=self.lang, symbols=symbols, edges=edges, loc=loc, hash=h)


register(GoParser())  # type: ignore[arg-type]
