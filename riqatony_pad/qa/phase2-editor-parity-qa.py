#!/usr/bin/env python3
"""RiqatonyPad 1.0.4 Audit 2 + Audit 9 convergence gate."""
from pathlib import Path
import ast
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
source=contract_text(ROOT)
source += '\n' + (ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
module=ast.parse(source)
cls=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=="RiqatonyPad")
methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
_commands_mixin=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='EditorCommandsAppearanceMixin')
_commands_methods={n.name:n for n in _commands_mixin.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(_commands_methods)
methods.update(_commands_methods)
insertion_source=(ROOT/"widgets/rwpyn/editor_insertion.py").read_text(encoding="utf-8")
insertion=next(n for n in ast.parse(insertion_source).body if isinstance(n,ast.ClassDef) and n.name=="EditorInsertionMixin")
insertion_methods={n.name:n for n in insertion.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(insertion_methods)
methods.update(insertion_methods)
ribbon_source=(ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
ribbon_cls=next(n for n in ast.parse(ribbon_source).body if isinstance(n,ast.ClassDef) and n.name=='EditorRibbonRetroMixin')
ribbon_methods={n.name:n for n in ribbon_cls.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(ribbon_methods)
methods.update(ribbon_methods)
search_source=(ROOT/"widgets/rwpyn/editor_search_view.py").read_text(encoding="utf-8")
search_cls=next(n for n in ast.parse(search_source).body if isinstance(n,ast.ClassDef) and n.name=="EditorSearchViewMixin")
search_methods={n.name:n for n in search_cls.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(search_methods)
methods.update(search_methods)
def seg(name):
    text=insertion_source if name in insertion_methods else search_source if name in search_methods else ribbon_source if name in ribbon_methods else source
    return ast.get_source_segment(text,methods[name]) or ""
# Audit 2: one transient two-row panel, not the old separate Replace dialog.
build=seg("build_ui")
for needle in (
    'self.search_container=QFrame(central)',
    'self.search_entry=QLineEdit(self.search_container); self.search_entry.setPlaceholderText("Find")',
    'self.replace_entry=QLineEdit(self.search_container); self.replace_entry.setPlaceholderText("Replace")',
    'self.search_case_checkbox=QCheckBox("Match case",self.search_container)',
    'self.search_previous_button=QPushButton("Previous",self.search_container)',
    'self.search_next_button=QPushButton("Next",self.search_container)',
    'self.search_replace_button=QPushButton("Replace",self.search_container)',
    'self.search_replace_all_button=QPushButton("Replace All",self.search_container)',
    'self.search_close_button=QPushButton("Close",self.search_container)',
): assert needle in build,needle
assert "_replace_dialog_closed" not in methods
assert "Find and Replace — RiqatonyPad" not in source
# 1.0.4 may relabel the menu entries; the unified panel behavior remains authoritative.
edit=seg("make_edit_menu")
assert 'QAction("Find",self)' in edit
assert 'menu,"Find and Replace"' in edit
assert 'QKeySequence.StandardKey.Find' in edit and 'QKeySequence("Ctrl+H")' in edit
# Find/Replace behavior and safety parity.
for name in ("toggle_find_panel","show_find_panel","hide_find_panel","refresh_search","replace_next","replace_all","find_next","find_previous"):
    assert name in methods,name
assert 'MAX_SEARCH_MATCHES = 10_000' in search_source
assert 'QColor("#C9A227")' in seg("refresh_search")
assert 'self.text_area.setTextCursor(active_cursor)' in seg("refresh_search")
assert 'MAX_DOCUMENT_CHARACTERS' in seg("replace_next") and 'MAX_DOCUMENT_CHARACTERS' in seg("replace_all")
assert 'beginEditBlock()' in seg("replace_all") and '_search_refresh_suspended=True' in seg("replace_all")
shortcuts=seg("bind_shortcuts")
for key in ('QKeySequence("F3")','QKeySequence("Shift+F3")','QKeySequence("Esc")'): assert key in shortcuts,key
# Existing four Editor Layout labels and placement algorithm remain intact.
view=seg("make_view_menu")
for label in ("Toolbar Top / Find Bottom","Toolbar Top / Find Top","Toolbar Bottom / Find Top","Toolbar Bottom / Find Bottom"):
    assert label in view,label
layout=seg("apply_workspace_layout")
for needle in (
    'self.main_layout.addWidget(interface); self.main_layout.addWidget(self.search_container); add_editor_block()',
    'add_editor_block(); self.main_layout.addWidget(self.search_container); self.main_layout.addWidget(interface)',
    'self.main_layout.addWidget(interface); add_editor_block(); self.main_layout.addWidget(self.search_container)',
    'self.main_layout.addWidget(self.search_container); add_editor_block(); self.main_layout.addWidget(interface)',
): assert needle in layout,needle
# Audit 9: exact 40-entry curated inventory, old 32 in order plus approved eight.
symbol_method=methods["show_symbols_popup"]
symbols=None
for node in ast.walk(symbol_method):
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="symbols" for t in node.targets):
        symbols=ast.literal_eval(node.value); break
assert symbols is not None and len(symbols)==40,len(symbols or ())
assert symbols[-8:]==("★","☆","♥","♦","♣","♠","☐","☑")
print("PASS: RiqatonyPad 1.0.4 Audit 2 Find/Replace + Audit 9 Symbols parity")
