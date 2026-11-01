#!/usr/bin/env python3
"""x6.0 preferences and new-document defaults extraction: frozen x5.0 AST parity."""
import ast, hashlib, json
from pathlib import Path
from source_contract import contract_text
APP=Path(__file__).resolve().parents[1]
DIR=APP/"."
DATA=json.loads((APP/'qa/x6-method-fingerprints.json').read_text(encoding='utf-8'))
parse=lambda path:ast.parse(contract_text(path.parent) if path.name=='app.py' else path.read_text(encoding='utf-8'))
cls=lambda path,name:next(n for n in parse(path).body if isinstance(n,ast.ClassDef) and n.name==name)
classes=[cls(DIR/"app.py","RiqatonyPad"),
 cls(DIR/'widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin'),
 cls(DIR/'widgets/rwpyn/editor_preferences.py','EditorPreferencesMixin'),
 cls(DIR/'widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin'),
 cls(DIR/'widgets/rwpyn/editor_printing.py','EditorPrintingMixin'),
 cls(DIR/'widgets/rwpyn/editor_search_view.py','EditorSearchViewMixin'),
 cls(DIR/'widgets/rwpyn/editor_formatting.py','EditorFormattingMixin'),
 cls(DIR/'widgets/rwpyn/editor_insertion.py','EditorInsertionMixin'),
 cls(DIR/"widgets/rwpyn/editor_lifecycle.py","EditorFileLifecycleMixin"),]
assert [ast.unparse(n) for n in classes[0].bases]==['EditorFileLifecycleMixin','EditorCommandsAppearanceMixin','EditorRibbonRetroMixin','EditorPreferencesMixin', 'EditorPrintingMixin', 'EditorSearchViewMixin', 'EditorFormattingMixin', 'EditorInsertionMixin', 'QMainWindow']
methods=[n for c in classes for n in c.body if isinstance(n,ast.FunctionDef)]
assert len(methods)==len({n.name for n in methods}), 'duplicate editor methods'
actual={m.name:hashlib.sha256(ast.dump(m,include_attributes=False).encode()).hexdigest() for m in methods}
assert actual==DATA['methods'], 'method lost/added/AST-changed from frozen x5.0'
assert {m.name for m in classes[2].body if isinstance(m,ast.FunctionDef)}==set(DATA['moved'])
source=parse(DIR/'widgets/rwpyn/editor_preferences.py')
original=parse(DIR/"app.py")
funcs={n.name:n for n in source.body if isinstance(n,ast.FunctionDef)}
for name,expected in DATA['helpers'].items():
    assert name in funcs
    node=funcs[name]
    if name=='resource_path':
        # The canonical assets directory remains at the application root,
        # now two directories above widgets/rwpyn/. Compare its original
        # implementation while normalising only that path-resolution change.
        import copy
        node=copy.deepcopy(node)
        paths=[x for x in ast.walk(node) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='script_dir' for t in x.targets)]
        assert len(paths)==1
        paths[0].value=ast.parse('os.path.dirname(os.path.abspath(__file__))',mode='eval').body
    assert hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()==expected
    assert not any(isinstance(n,ast.FunctionDef) and n.name==name for n in original.body)
assign=lambda tree,name:next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
assert ast.dump(assign(source,'MAX_CONFIG_FILE_SIZE').value,include_attributes=False)==DATA['max_config']
assert not any(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MAX_CONFIG_FILE_SIZE' for t in n.targets) for n in original.body)

# The original, unmodified Retro configuration constants are bound at import-time.
assert any(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RETRO_TOOLBAR_DEFAULT' for t in n.targets) for n in parse(DIR/'widgets/editor_commands_appearance.py').body)
assert any(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RETRO_TOOLBAR_ALLOWED' for t in n.targets) for n in parse(DIR/'widgets/editor_commands_appearance.py').body)
text=(DIR/'app.py').read_text(encoding='utf-8')
assert '_editor_preferences.RETRO_TOOLBAR_DEFAULT = RETRO_TOOLBAR_DEFAULT' in text
assert '_editor_preferences.RETRO_TOOLBAR_ALLOWED = RETRO_TOOLBAR_ALLOWED' in text

print('PASS: x6.0 eleven preferences/defaults methods, three helpers and prior editor ASTs preserved')
