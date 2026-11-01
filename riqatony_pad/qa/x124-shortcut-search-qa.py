#!/usr/bin/env python3
"""x12.4: exact helper-source preservation, canonical import topology and behaviour."""
from __future__ import annotations
from pathlib import Path
import ast, hashlib, importlib.util, sys
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'shortcut_tokens': '3a9f9b687fb53a820c7f891c6a6b462401c5b3afcbd634d57c7021c4edfb6bcc', 'shortcut_query_matches': '9dc2879b41a1884ef8f8c4960a2148afcf05171ec8c4502052b113189fe29848'}
VERSION='2.0.0-x13.0'
MAQ=False
TARGET=ROOT/'widgets/editor_commands_appearance.py'
IMPORT='from widgets.keyboard_shortcuts import shortcut_query_matches, shortcut_tokens'
TOKEN='shortcut_tokens'
MATCH='shortcut_query_matches'
MODULE=ROOT/'widgets/keyboard_shortcuts.py'
assert MODULE.is_file() and not (ROOT/'shortcut_search.py').exists()
source=MODULE.read_text(encoding='utf-8')
assert source.startswith('#!/usr/bin/env python3\n')
tree=ast.parse(source)
expected=EXPECTED
methods={n.name:hashlib.sha256(ast.get_source_segment(source,n).encode()).hexdigest() for n in tree.body if isinstance(n,ast.FunctionDef)}
assert {key:methods[key] for key in expected}==expected, ('original helper definition changed', methods)
app=(ROOT/'app.py').read_text()
assert 'APP_VERSION = "'+VERSION+'"' in app
assert 'shortcut_tokens(' in MODULE.read_text(), 'shortcut query tokenisation is missing'
assert not (ROOT/'app.py').read_text().count('def _shortcut_tokens('), 'duplicate MaqaronyPad helper'
assert 'from shortcut_search import' not in app, 'obsolete root-level helper import'
if not MAQ:
    assert '_keyboard_shortcuts.show_keyboard_shortcuts_dialog' in app, 'main window shortcut-dialog binding missing'
# Import the pure helper module without PyQt or application globals.
spec=importlib.util.spec_from_file_location('x124_shortcut_search',MODULE)
obj=importlib.util.module_from_spec(spec)
spec.loader.exec_module(obj)
tokens=getattr(obj,TOKEN)('Ctrl+Alt+Shift+N')
match=getattr(obj,MATCH)
assert match('shift control n',tokens)
assert match('ctl n',tokens)
assert match('alt shift',tokens)
assert not match('meta q',tokens)
assert not match('',tokens)
assert all(p.read_bytes().startswith(b'#!/usr/bin/env python3') for p in ROOT.rglob('*.py'))
builder=(ROOT/'packaging/fedora/build-appimage.sh').read_text()
assert 'widgets/keyboard_shortcuts.py' in builder or 'collect_submodules' in builder or 'compileall -q "$SOURCE_ENTRY" "$PROGRAM_ROOT"' in builder
assert (ROOT/'widgets/window_search_view.py').exists() == MAQ
print('PASS x12.4: shortcut helpers are exact copies, canonical, importable and behaviour-preserving')
