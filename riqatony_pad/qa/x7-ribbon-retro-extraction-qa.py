#!/usr/bin/env python3
"""x7.0 presentation extraction: unchanged x6.0 method/class AST fingerprints."""
from pathlib import Path
import ast,hashlib,json
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'qa/x7-method-fingerprints.json').read_text())
assert DATA['baseline']=='2.0.0-x6.0'
parse=lambda p:ast.parse(contract_text(ROOT) if p=='app.py' else (ROOT/p).read_text(encoding='utf-8'))
class_of=lambda file,name:next(n for n in parse(file).body if isinstance(n,ast.ClassDef) and n.name==name)
files=[('app.py','RiqatonyPad'),('widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin'),('widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin'),('widgets/rwpyn/editor_preferences.py','EditorPreferencesMixin'),('widgets/rwpyn/editor_printing.py','EditorPrintingMixin'),('widgets/rwpyn/editor_search_view.py','EditorSearchViewMixin'),('widgets/rwpyn/editor_formatting.py','EditorFormattingMixin'),('widgets/rwpyn/editor_insertion.py','EditorInsertionMixin'),('widgets/rwpyn/editor_lifecycle.py','EditorFileLifecycleMixin')]
classes=[class_of(*item) for item in files]
assert [ast.unparse(n) for n in classes[0].bases]==['EditorFileLifecycleMixin','EditorCommandsAppearanceMixin','EditorRibbonRetroMixin','EditorPreferencesMixin','EditorPrintingMixin','EditorSearchViewMixin','EditorFormattingMixin','EditorInsertionMixin','QMainWindow']
methods=[m for c in classes for m in c.body if isinstance(m,ast.FunctionDef)]
assert len(methods)==len({m.name for m in methods})
dig=lambda node:hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
assert {m.name:dig(m) for m in methods}==DATA['methods'],'existing method AST changed/lost/added'
assert {m.name for m in classes[2].body if isinstance(m,ast.FunctionDef)}==set(DATA['moved'])
scroll=class_of('widgets/editor_ribbon_retro.py','RibbonScrollArea')
assert dig(scroll)==DATA['ribbon_scroll_area']
assert not any(isinstance(n,ast.ClassDef) and n.name=='RibbonScrollArea' for n in parse('app.py').body)
host=contract_text(ROOT)
assert 'from widgets.editor_ribbon_retro import EditorRibbonRetroMixin, RibbonScrollArea' in host
assert '_editor_ribbon_retro.RETRO_TOOLBAR_DEFAULT = RETRO_TOOLBAR_DEFAULT' in host
for name in ('RIBBON_BUTTON_SIZE','RIBBON_ICON_SIZE','RIBBON_FONT_FAMILY_WIDTH'):
    assert not any(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets) for n in parse('app.py').body)
assert 'RIBBON_BUTTON_SIZE = 52' in (ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
assert 'RIBBON_ICON_SIZE = 36' in (ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
assert 'RIBBON_FONT_FAMILY_WIDTH = RIBBON_BUTTON_SIZE * 2' in (ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
print('PASS: x7.0 RibbonScrollArea and 24 presentation methods exact x6.0 AST parity; all other editor methods unchanged')
