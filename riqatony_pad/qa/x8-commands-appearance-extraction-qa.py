#!/usr/bin/env python3
"""x8.0 command/icon/appearance extraction — original complete-editor AST parity."""
import ast, json, hashlib
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'' if False else ROOT
DATA=json.loads((ROOT/'qa/x8-method-fingerprints.json').read_text(encoding='utf-8'))
assert DATA['baseline']=='2.0.0-x7.0'
parse=lambda name:ast.parse(contract_text(DIR) if name=='app.py' else (DIR/name).read_text(encoding='utf-8'))
cls=lambda name,label:next(n for n in parse(name).body if isinstance(n,ast.ClassDef) and n.name==label)
classes=[cls('app.py','RiqatonyPad'),
 cls('widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin'),
 cls('widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin'),
 cls('widgets/rwpyn/editor_preferences.py','EditorPreferencesMixin'),
 cls('widgets/rwpyn/editor_printing.py','EditorPrintingMixin'),
 cls('widgets/rwpyn/editor_search_view.py','EditorSearchViewMixin'),
 cls('widgets/rwpyn/editor_formatting.py','EditorFormattingMixin'),
 cls('widgets/rwpyn/editor_insertion.py','EditorInsertionMixin'),
 cls('widgets/rwpyn/editor_lifecycle.py','EditorFileLifecycleMixin'),]
methods=[method for c in classes for method in c.body if isinstance(method,ast.FunctionDef)]
assert len(methods)==len({method.name for method in methods}),'method duplicate'
get_hash=lambda node:hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
assert {m.name:get_hash(m) for m in methods if m.name in DATA['methods']}==DATA['methods'],'original editor method changed, lost or added'
assert {m.name for m in classes[1].body if isinstance(m,ast.FunctionDef)}==set(DATA['moved']),'wrong x8 extraction inventory'
assert 'RiqatonyPad'==DATA['original_host_class']
host=(DIR/'app.py').read_text(encoding='utf-8')
assert 'from widgets.editor_commands_appearance import EditorCommandsAppearanceMixin' in host
original=parse('app.py')
commands=parse('widgets/editor_commands_appearance.py')
for name in ('RETRO_TOOLBAR_DEFAULT','COMMAND_SURFACE_SPECS','RETRO_TOOLBAR_ALLOWED'):
    assert any(isinstance(n,(ast.Assign,ast.AnnAssign)) and any(isinstance(t,ast.Name) and t.id==name for t in getattr(n,'targets',())) for n in commands.body),name
    assert not any(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets) for n in original.body),name
assert '_editor_commands_appearance.OPEN_WINDOWS = OPEN_WINDOWS' in host
print('PASS: 2.0.0-x8.0 — 28 moved command/appearance methods and all other baseline editor methods AST unchanged')
