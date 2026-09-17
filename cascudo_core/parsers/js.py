"""Parser JS/TS — tree-sitter-languages, 0 IA, determinístico."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from . import Edge, ParseResult, Symbol, register

try:
    from tree_sitter_languages import get_language, get_parser  # type: ignore

    _HAS_TS = True
except Exception:  # fallback regex se lib não instalada no lint
    _HAS_TS = False

# Regex fallback (MVP rápido) — cobre 80% sem tree-sitter instalado
_RE_FUNC = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(|"
    r"^\s*(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|"
    r"^\s*(?:export\s+)?class\s+(\w+)",
    re.MULTILINE,
)
_RE_IMPORT = re.compile(r'^\s*import\s+.*from\s+["\'](.+)["\']', re.MULTILINE)
_RE_CALL = re.compile(r"(\w+)\s*\(")
_RE_EXPORT = re.compile(r"^\s*export\s+", re.MULTILINE)
_RE_ENTRY = re.compile(r"(main|index|app|server)\.(js|ts|jsx|tsx)$")


def _cc_simple(body: str) -> int:
    # CC aproximado: count if/for/while/case/&&/||/? +1
    kws = len(re.findall(r"\b(if|for|while|case|catch)\b|&&|\|\||\?", body))
    return kws + 1


class JSParser:
    lang = "js"
    extensions = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    def parse(self, path: Path, content: str) -> ParseResult:
        file_s = str(path)
        loc = content.count("\n") + 1
        h = hashlib.sha256(content.encode()).hexdigest()[:12]
        symbols: list[Symbol] = []
        edges: list[Edge] = []

        is_entry = bool(_RE_ENTRY.search(file_s))

        # Fallback regex (funciona sem tree-sitter)
        for m in _RE_FUNC.finditer(content):
            name = next(g for g in m.groups() if g)
            line = content[: m.start()].count("\n") + 1
            # snippet até próximo \n\n para CC
            snippet = content[m.start() : m.start() + 800]
            symbols.append(
                Symbol(
                    kind="function" if "class" not in m.group(0) else "class",
                    name=name,
                    qualified_name=f"{path.stem}.{name}",
                    file=file_s,
                    line=line,
                    col=m.start() - content.rfind("\n", 0, m.start()),
                    cc=_cc_simple(snippet),
                    is_entrypoint=is_entry and name in ("main", "start", "init"),
                    is_exported=bool(_RE_EXPORT.search(m.group(0))),
                    lang=self.lang,
                )
            )

        for m in _RE_IMPORT.finditer(content):
            target = m.group(1)
            line = content[: m.start()].count("\n") + 1
            edges.append(
                Edge(
                    kind="IMPORTS",
                    source=file_s,
                    target=target,
                    file=file_s,
                    line=line,
                    confidence="high",
                )
            )

        # CALLS intra-file: extrai corpo entre {} para evitar falsos
        func_names = {s.name for s in symbols}
        snippets: dict[str, str] = {}

        def _body(start: int) -> str:
            # encontra primeiro { e seu } correspondente
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

        for m, s in zip(_RE_FUNC.finditer(content), symbols):
            snippets[s.qualified_name] = _body(m.start())
        for s in symbols:
            body = snippets.get(s.qualified_name, "")
            # remove definição para não contar como call
            body_no_def = re.sub(r"function\s+\w+\s*\(", "", body)
            for cm in _RE_CALL.finditer(body_no_def):
                callee = cm.group(1)
                if callee in func_names and callee != s.name:
                    # evita keywords
                    if callee in ("if", "for", "while", "switch", "catch", "return", "console"):
                        continue
                    # verifica não é 'function foo' (definição)
                    before = body_no_def[max(0, cm.start() - 12) : cm.start()]
                    if "function" in before or "class" in before:
                        continue
                    edges.append(
                        Edge(
                            kind="CALLS",
                            source=s.qualified_name,
                            target=f"{path.stem}.{callee}",
                            file=file_s,
                            line=s.line,
                            confidence="medium",
                        )
                    )

        # Se tree-sitter disponível, tentaria refining aqui (mantém interface)
        if _HAS_TS:
            try:
                # placeholder para refinamento futuro — não quebra se falhar
                from tree_sitter_languages import get_language as _get_lang, get_parser as _get_parser  # type: ignore

                lang = _get_lang("javascript")
                parser = _get_parser("javascript")
                tree = parser.parse(bytes(content, "utf8"))
                # TODO: queries S-expression para extrair com precisão
                _ = (lang, tree)
            except Exception:
                pass

        return ParseResult(file=file_s, lang=self.lang, symbols=symbols, edges=edges, loc=loc, hash=h)


register(JSParser())  # type: ignore[arg-type]
