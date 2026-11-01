#!/usr/bin/env python3
"""Static regression gate for the Delete Line corruption fixed in 0.7.3-exp1-r2-r1.

The runtime test covers the six manually reproduced ordinary/list and
empty/non-empty middle/final cases. This gate prevents the unsafe unconditional
second character deletion from being reintroduced.
"""
from pathlib import Path
import ast

source_path = Path(__file__).resolve().parents[1] / "widgets/rwpyn/editor_insertion.py"
source = source_path.read_text(encoding="utf-8")
tree = ast.parse(source)
method = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "delete_current_line":
        method = node
        break
assert method is not None, "delete_current_line() missing"
segment = ast.get_source_segment(source, method) or ""
assert "cursor.select(QTextCursor.SelectionType.BlockUnderCursor)" in segment
assert "if cursor.hasSelection():" in segment, "non-empty/empty block split missing"
assert "cursor.removeSelectedText()" in segment
assert "elif is_last and has_previous:" in segment
assert "cursor.deletePreviousChar()" in segment
assert "elif not is_last:" in segment
assert "cursor.deleteChar()" in segment

unsafe = "cursor.removeSelectedText()\n            if is_last and has_previous:"
assert unsafe not in segment, "unsafe unconditional cleanup deletion reintroduced"
print("delete-line-qa: PASS")
