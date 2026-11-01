#!/usr/bin/env python3
"""Dependency-free on-demand word-count regression gate for RiqatonyPad 1.0.4."""
from __future__ import annotations

import ast
import re
from pathlib import Path

from source_contract import contract_text
root = Path(__file__).resolve().parents[1]
source = contract_text(root)
module = ast.parse(source)
printing = (root / "widgets/rwpyn/editor_printing.py").read_text(encoding="utf-8")
printing_tree = ast.parse(printing)
parts = []
for node in printing_tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_WORD_COUNT_RE" for t in node.targets):
        parts.append(ast.get_source_segment(printing, node))
    elif isinstance(node, ast.FunctionDef) and node.name == "count_words":
        parts.append(ast.get_source_segment(printing, node))
assert len(parts) == 2, parts
namespace = {"re": re}
exec("\n\n".join(parts), namespace)
count_words = namespace["count_words"]

cases = {
    "": 0,
    "   \n\t": 0,
    "one": 1,
    "one two three": 3,
    "don't stop": 2,
    "don’t stop": 2,
    "state-of-the-art editor": 2,
    "Hello, world! (Again.)": 3,
    "naïve café résumé": 3,
    "中文 測試": 2,
    "alpha\n\n beta\t gamma": 3,
    "rock-'n'-roll": 3,
}
for text, expected in cases.items():
    observed = count_words(text)
    assert observed == expected, (text, observed, expected)

# Word count must remain on-demand in Properties, never on textChanged/cursor updates.
riqatonypad = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "RiqatonyPad")
methods = {node.name: ast.get_source_segment(source, node) or "" for node in riqatonypad.body if isinstance(node, ast.FunctionDef)}
search= (root/"widgets/rwpyn/editor_search_view.py").read_text(encoding="utf-8")
search_cls=next(node for node in ast.parse(search).body if isinstance(node,ast.ClassDef) and node.name=="EditorSearchViewMixin")
search_methods={node.name:ast.get_source_segment(search,node) or "" for node in search_cls.body if isinstance(node,ast.FunctionDef)}
assert not set(methods)&set(search_methods)
methods.update(search_methods)
print_cls=next(node for node in printing_tree.body if isinstance(node,ast.ClassDef) and node.name=="EditorPrintingMixin")
print_methods={node.name:ast.get_source_segment(printing,node) or "" for node in print_cls.body if isinstance(node,ast.FunctionDef)}
assert not set(methods)&set(print_methods)
methods.update(print_methods)
assert "count_words(text)" in methods["show_properties_dialog"]
assert "count_words" not in methods["on_document_text_changed"]
assert "count_words" not in methods["update_status_counts"]
print("PASS: RiqatonyPad 1.0.4 on-demand Unicode-aware word count")
