"""Parsers strategy — cada linguagem é uma strategy com tree-sitter query."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Symbol:
    kind: str  # function | class | method | route | variable | import
    name: str
    qualified_name: str
    file: str
    line: int
    col: int
    cc: int = 1
    is_entrypoint: bool = False
    is_exported: bool = False
    lang: str = "js"


@dataclass(frozen=True)
class Edge:
    kind: str  # CALLS | IMPORTS | CONTAINS | INHERITS
    source: str  # qualified_name
    target: str
    file: str
    line: int
    confidence: str = "high"


@dataclass
class ParseResult:
    file: str
    lang: str
    symbols: list[Symbol] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    loc: int = 0
    hash: str = ""


class Parser(Protocol):
    lang: str
    extensions: tuple[str, ...]  # type: ignore[override]

    def can_parse(self, path: Path) -> bool: ...
    def parse(self, path: Path, content: str) -> ParseResult: ...


# Registry escalável — adicionar linguagem = 1 classe + 1 linha register
_REGISTRY: dict[str, Parser] = {}


def register(parser: object) -> None:
    exts = getattr(parser, "extensions", ())
    for ext in exts:  # type: ignore
        _REGISTRY[ext] = parser  # type: ignore


def get_parser(path: Path) -> Parser | None:
    return _REGISTRY.get(path.suffix.lower())


def supported_langs() -> list[str]:
    return sorted({p.lang for p in _REGISTRY.values()})
