"""Walker — varre diretório/zip, parseia via registry, retorna ParseResults."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

from .parsers import ParseResult, get_parser

# importa parsers para registrar — side-effect (escalável: add linha = add linguagem)
from .parsers import c as _c  # noqa: F401
from .parsers import go as _go  # noqa: F401
from .parsers import java as _java  # noqa: F401
from .parsers import js as _js  # noqa: F401
from .parsers import python as _py  # noqa: F401
from .parsers import rust as _rs  # noqa: F401


IGNORE_DIRS = {".git", "node_modules", ".venv", "dist", "build", "__pycache__", ".next", ".turbo"}
IGNORE_EXTS = {".json", ".md", ".txt", ".lock", ".png", ".jpg", ".svg", ".ico"}


def _should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts) or path.suffix.lower() in IGNORE_EXTS


def walk_and_parse(root: Path, max_files: int = 20000, max_bytes: int = 100 * 1024 * 1024) -> list[ParseResult]:
    results: list[ParseResult] = []
    total_bytes = 0

    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _should_ignore(p):
            continue
        parser = get_parser(p)
        if not parser:
            # fallback File node (sem parser) — ainda conta como file
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                loc = content.count("\n") + 1
                h = hashlib.sha256(content.encode()).hexdigest()[:12]
                results.append(ParseResult(file=str(p), lang="unknown", symbols=[], edges=[], loc=loc, hash=h))
            except Exception:
                continue
            continue

        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            total_bytes += len(content.encode())
            if total_bytes > max_bytes:
                break
            if len(results) >= max_files:
                break
            # limite 500KB por arquivo (evita bundle)
            if len(content) > 500_000:
                content = content[:500_000]
            results.append(parser.parse(p, content))
        except Exception:
            continue

    return results


def parse_zip(zip_path: Path, extract_to: Path) -> list[ParseResult]:
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)
    return walk_and_parse(extract_to)
