#!/usr/bin/env python3
"""x10.0 file-lifecycle extraction: exact full-editor parity against the prior issued baseline."""
import ast,hashlib,json
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'qa/x10-method-fingerprints.json').read_text(encoding='utf-8'))
EXPECTED_BASELINE='2.0.0-x9.0'
assert DATA['baseline']==EXPECTED_BASELINE
LOCATIONS=[('app.py', 'RiqatonyPad'), ('widgets/rwpyn/editor_lifecycle.py', 'EditorFileLifecycleMixin'), ('widgets/editor_commands_appearance.py', 'EditorCommandsAppearanceMixin'), ('widgets/editor_ribbon_retro.py', 'EditorRibbonRetroMixin'), ('widgets/rwpyn/editor_preferences.py', 'EditorPreferencesMixin'), ('widgets/rwpyn/editor_printing.py', 'EditorPrintingMixin'), ('widgets/rwpyn/editor_search_view.py', 'EditorSearchViewMixin'), ('widgets/rwpyn/editor_formatting.py', 'EditorFormattingMixin'), ('widgets/rwpyn/editor_insertion.py', 'EditorInsertionMixin')]
get_cls=lambda file,name: next(n for n in ast.parse((contract_text(ROOT) if file=='app.py' else (ROOT/file).read_text(encoding='utf-8'))).body if isinstance(n,ast.ClassDef) and n.name==name)
classes=[get_cls(*tup) for tup in LOCATIONS]
methods=[m for c in classes for m in c.body if isinstance(m,ast.FunctionDef)]
names=[m.name for m in methods]
assert len(names)==len(set(names)), 'duplicate editor methods after extraction'
digest=lambda m: hashlib.sha256(ast.dump(m,include_attributes=False).encode()).hexdigest()
assert {m.name:digest(m) for m in methods if m.name in DATA['methods']}==DATA['methods'], 'baseline editor method changed, added, or lost'
assert {m.name for m in classes[1].body if isinstance(m,ast.FunctionDef)}==set(DATA['moved']), 'lifecycle extraction inventory drift'
assert not set(DATA['moved']) & {m.name for m in classes[0].body if isinstance(m,ast.FunctionDef)}, 'lifecycle methods duplicated in host'
host=(ROOT/('app.py' if DATA['origin']=='riqatonypad.py' else DATA['origin'])).read_text(encoding='utf-8')
assert 'EditorFileLifecycleMixin' in host
assert 'MAX_FILE_SIZE, RTF_EXTENSIONS, DOCUMENT_EXTENSIONS' in host
assert [ast.unparse(b) for b in classes[0].bases][0]=='EditorFileLifecycleMixin', 'mixin method resolution changed'
print('PASS: x10.0 complete editor AST, original file lifecycle safeguards, and method ownership preserved')
