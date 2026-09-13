"""The language audit (ADR-0001): comments and docstrings are English.

Quoted spans may be French — a comment names the prompt text, a warning or
a bible term it talks about — and so may isolated French terms; everything
else is checked against a French stopword list. The audit is falsified here
against a French sample before the repository is held to it.
"""

import ast
import io
import re
import tokenize
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ROOTS = (REPO / "src" / "factory", REPO / "tests")

# Stopwords only, no accent check: an English comment legitimately names French
# terms (passé simple, régime, « heures ») when it explains a detector or a prompt.
FRENCH = re.compile(
    r"\b(le|la|les|des|une|est|pour|dans|pas|que|qui|sur|avec|par|sont|mais|donc|"
    r"cette|aux|du|elle|ne|sans|entre|jamais|toujours|même|après|avant|depuis|"
    r"chaque|nous|servi|servie|appel|nœud|fiche|chapitre|modèle|phrase|texte|mot|mots|"
    r"c'est|d'un|d'une)\b", re.IGNORECASE)
QUOTED = re.compile(r"«[^»]*»|“[^”]*”|``[^`]*``|`[^`]*`|\"[^\"]*\"|'[^']*'")


def french_lines(source: str) -> list[tuple[int, str]]:
    """(line, text) of every comment or docstring line that reads as French."""
    hits: list[tuple[int, str]] = []
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT and FRENCH.search(QUOTED.sub("", tok.string)):
            hits.append((tok.start[0], tok.string.strip()))
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if not doc:
                continue
            first = node.body[0].lineno
            for i, line in enumerate(doc.splitlines()):
                if FRENCH.search(QUOTED.sub("", line)):
                    hits.append((first + i, line.strip()))
    return hits


def test_the_audit_fires_on_french_and_accepts_quoted_french():
    assert french_lines("# le texte est servi ici\nx = 1\n")
    assert french_lines('def f():\n    """Compose la phrase pour le modèle."""\n')
    assert french_lines("# the word « couperet » — the model wrote it, see the run\nx = 1\n") == []
    assert french_lines("# cut at the brief's ``**Entrée N`` headings, passé simple only\n") == []
    assert french_lines('s = "le texte en français reste dans la chaîne"\n') == []


@pytest.mark.parametrize("path", [p for root in ROOTS for p in sorted(root.rglob("*.py"))],
                         ids=lambda p: str(p.relative_to(REPO)))
def test_comments_and_docstrings_are_english(path):
    hits = french_lines(path.read_text(encoding="utf-8"))
    assert not hits, "\n".join(f"{path.relative_to(REPO)}:{ln}: {txt}" for ln, txt in hits)
