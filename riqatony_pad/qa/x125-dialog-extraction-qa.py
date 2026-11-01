#!/usr/bin/env python3
"""x12.5: exact dialog method relocations, live host bindings and shortcut consolidation."""
from __future__ import annotations
import ast, hashlib, json, symtable, builtins
from pathlib import Path
from shortcut_legacy import legacy_read_bytes
ROOT=Path(__file__).resolve().parents[1]
METHODS = [('about_dialog', 'show_about_dialog'), ('quick_tour', 'show_tutorial_wizard'), ('keyboard_shortcuts', 'show_keyboard_shortcuts_dialog')]
EXPECTED_CLASS = 'RiqatonyPad'
EXPECTED_VERSION = '2.0.0-x13.0'
source=(ROOT/'app.py').read_text(encoding='utf-8')
assert f'APP_VERSION = "{EXPECTED_VERSION}"' in source
cls=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name==EXPECTED_CLASS)
attr_bindings={n.targets[0].id:n.value for n in cls.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
expected=json.loads((ROOT/'qa/x125-method-fingerprints.json').read_text())
assert set(expected)=={name for module,name in METHODS}
assert not any(isinstance(n,ast.FunctionDef) and n.name in expected for n in cls.body),'old methods still duplicated in app.py'
assert len(attr_bindings)==len(set(attr_bindings))
for module,name in METHODS:
    node=attr_bindings.get(name)
    assert isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name),f'{name}: binding missing'
    assert node.value.id=='_'+module and node.attr==name,f'{name}: incorrect binding'
    src=(ROOT/'widgets'/f'{module}.py').read_text(encoding='utf-8')
    matches=[n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name==name]
    assert len(matches)==1,f'{name}: lost or duplicated implementation'
    definition=ast.get_source_segment(src,matches[0])
    assert hashlib.sha256((definition+'\n').encode()).hexdigest()==expected[name],f'{name}: body changed'
    assert f'import widgets.{module} as _{module}' in source,f'{module}: app import missing'
    # Check every referenced global resolves through Qt imports, helpers, builtins or explicit host injection.
    sym=symtable.symtable(src,str(module),'exec').lookup(name).get_namespace()
    needed={s.get_name() for s in sym.get_symbols() if s.is_global() and s.is_referenced()}
    local={x.name for x in ast.parse(src).body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
    imports=set()
    for top in ast.walk(ast.parse(src)):
        if isinstance(top,ast.Import): imports.update(alias.asname or alias.name.split('.')[0] for alias in top.names)
        if isinstance(top,ast.ImportFrom): imports.update(alias.asname or alias.name for alias in top.names)
        if isinstance(top,(ast.Assign,ast.AnnAssign)):
            for lhs in (top.targets if isinstance(top,ast.Assign) else [top.target]):
                imports.update(n.id for n in ast.walk(lhs) if isinstance(n,ast.Name))
    injected={n.attr for n in ast.parse(source).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='_'+module for t in n.targets) for n in n.targets if isinstance(n,ast.Attribute)}
    unresolved=needed-(local|imports|injected|set(dir(builtins)))
    assert not unresolved,(module,name,'unbound globals',unresolved)
shortcut=ROOT/'widgets/keyboard_shortcuts.py'
assert shortcut.is_file() and not (ROOT/'widgets/shortcut_search.py').exists()
assert not 'widgets.shortcut_search' in source
raw=shortcut.read_bytes();length=int((ROOT/'qa/x125-helper-length.txt').read_text())
assert hashlib.sha256(raw[:length]).hexdigest()==(ROOT/'qa/x125-shortcut-helper.sha256').read_text().strip(),'original helper prefix changed'
assert (ROOT/'widgets/about_dialog.py').exists() and (ROOT/'widgets/quick_tour.py').exists()
print('PASS x12.5: method bodies, bindings, globals, helpers and canonical modules verified')
