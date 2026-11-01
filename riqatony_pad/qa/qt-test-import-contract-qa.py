#!/usr/bin/env python3
"""Guard actual Qt QA imports across the riqatonypad.py -> app.py rename.

Does not require PyQt6; must run even when Qt-backed tests are skipped. Checks
both real active tests, the app host symbol contract, and the Fedora runner.
"""
from __future__ import annotations
import ast
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = {
    'highlight-runtime-qa.py': {'RiqatonyPad'},
    'qt-rtf-qa.py': {'RiqatonyPad', 'OPEN_WINDOWS', 'RIQATONYPAD_INLINE_RICH_MIME', 'RichTextEdit'},
}
BUILDER = (ROOT/'packaging/fedora/build-appimage.sh').read_text(encoding='utf-8')
STATIC = (ROOT/'qa/static-qa.sh').read_text(encoding='utf-8')
SOURCE = (ROOT/'app.py').read_text(encoding='utf-8')
HOST = ast.parse(SOURCE)
# Exports can be defined directly or re-exported by explicit imports.
exports = set()
for node in HOST.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        exports.add(node.name)
    elif isinstance(node, ast.ImportFrom):
        exports.update(a.asname or a.name for a in node.names)
    elif isinstance(node, ast.Import):
        exports.update(a.asname or a.name.split('.')[0] for a in node.names)
    elif isinstance(node, (ast.Assign, ast.AnnAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                exports.add(target.id)

sys.path.insert(0,str(ROOT))
try:
    spec=importlib.util.find_spec('app')
    assert spec is not None and pathlib.Path(spec.origin).resolve() == (ROOT/'app.py').resolve()
finally:
    sys.path.remove(str(ROOT))

# The production app lazily imports its message helper using the absolute
# source-package name; check that independent Qt QA scripts can resolve it.
sys.path.insert(0, str(ROOT.parent))
try:
    helper=importlib.util.find_spec('riqatony_pad.widgets.message_conventions')
    assert helper is not None and pathlib.Path(helper.origin).resolve() == (ROOT/'widgets/message_conventions.py').resolve()
finally:
    sys.path.remove(str(ROOT.parent))


def verify(script: str, source: str, symbols: set[str]):
    tree = ast.parse(source, filename=script)
    host_imports = [node for node in tree.body if isinstance(node, ast.Import)
                    and any(a.name in ('app','riqatonypad') for a in node.names)]
    from_imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)
                    and node.module in ('app','riqatonypad')]
    assert len(host_imports)==1, f'{script}: missing/duplicate host-module import'
    assert len(from_imports)==1, f'{script}: missing/duplicate host symbols import'
    assert [(a.name,a.asname) for a in host_imports[0].names]==[('app','riqatonypad_module')], f'{script}: obsolete or unexpected host import'
    assert from_imports[0].module == 'app', f'{script}: obsolete QA host module'
    actual={alias.name for alias in from_imports[0].names}
    assert actual==symbols, f'{script}: unexpected app exports {actual} != {symbols}'
    assert actual <= exports, f'{script}: missing source symbols: {actual-exports}'
    assert not (ROOT/'riqatonypad.py').exists(), 'Obsolete app module reintroduced'
    # Compile the real source rather than merely checking its textual imports.
    compile(source, script, 'exec')

for script, symbols in SCRIPTS.items():
    source=(ROOT/'qa'/script).read_text(encoding='utf-8')
    verify(script,source,symbols)
    assert 'sys.path.insert(0, str(' in source
    assert '.parent))' in source, f'{script}: outer Portable package lookup path missing'
    # Prove this gate rejects the original pre-x16.8 import defect.
    broken=source.replace('import app as riqatonypad_module',
                          'import riqatonypad as riqatonypad_module',1)
    try:
        verify(script,broken,symbols)
    except AssertionError:
        pass
    else:
        raise AssertionError(f'{script}: regression check failed its negative test')

assert 'QT_RTF_QA="${PROGRAM_ROOT}/qa/qt-rtf-qa.py"' in BUILDER
assert 'QT_HIGHLIGHT_QA="${PROGRAM_ROOT}/qa/highlight-runtime-qa.py"' in BUILDER
for command in ('"$VENV/bin/python" "$QT_RTF_QA"', '"$VENV/bin/python" "$QT_HIGHLIGHT_QA"'):
    assert command in BUILDER, f'Fedora builder omitted required runtime test: {command}'
assert 'python3 "$ROOT/qa/qt-test-import-contract-qa.py"' in STATIC
assert 'python3 "$ROOT/qa/highlight-runtime-qa.py"' in STATIC
print('PASS: both Qt runtime QA modules import current app.py; missing historical import rejected; isolated Fedora Qt runner covers both')
