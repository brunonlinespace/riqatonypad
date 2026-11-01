#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.4 shared shell parity gate."""
from __future__ import annotations
import ast
from pathlib import Path
from source_contract import contract_text
root=Path(__file__).resolve().parents[1]
source=contract_text(root)
source += '\n' + (root/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
ribbon_source=(root/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
ribbon_tree=ast.parse(ribbon_source)
ribbon_cls=next(n for n in ribbon_tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorRibbonRetroMixin')
ribbon_methods={n.name:n for n in ribbon_cls.body if isinstance(n,ast.FunctionDef)}

module=ast.parse(source)
riqatonypad=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
methods={n.name:n for n in riqatonypad.body if isinstance(n,ast.FunctionDef)}
_commands_mixin=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='EditorCommandsAppearanceMixin')
_commands_methods={n.name:n for n in _commands_mixin.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(_commands_methods)
methods.update(_commands_methods)
printing=(Path(__file__).resolve().parents[1]/'widgets/rwpyn/editor_printing.py').read_text(encoding='utf-8')
print_cls=next(n for n in ast.parse(printing).body if isinstance(n,ast.ClassDef) and n.name=='EditorPrintingMixin')
print_methods={n.name:ast.get_source_segment(printing,n) or '' for n in print_cls.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(print_methods)
def seg(name): return print_methods[name] if name in print_methods else (ast.get_source_segment(ribbon_source,ribbon_methods[name]) or '') if name in ribbon_methods else (ast.get_source_segment(source,methods[name]) or '')
file_menu=seg('make_file_menu'); edit=seg('make_edit_menu'); view=seg('make_view_menu'); settings=seg('make_settings_menu'); ribbon=seg('build_ribbon'); lock=seg('toggle_view_only'); status=seg('update_status_counts'); props=seg('show_properties_dialog'); title=seg('update_title')
# Shared file/edit commands and shortcut choices remain converged.
assert 'self.more_actions_menu = menu.addMenu("More Actions")' in file_menu
assert file_menu.index('"Duplicate File…"') < file_menu.index('"Rename File…"') < file_menu.index('"Delete File"') < file_menu.index('"Open in External Editor"') < file_menu.index('"Open Containing Folder"') < file_menu.index('"Properties"')
assert 'QKeySequence("F4")' in file_menu and 'QKeySequence("Ctrl+Shift+D")' in file_menu
assert 'QKeySequence("Ctrl+D")' in edit and 'menu.addAction(self.search_bar_action)' in edit
# 1.0.4 retains standalone UI selectors in View and app-level selectors in Settings.
for required in ('menu.addMenu("Editor Layout")','menu.addMenu("Editor Toolbar")','menu.addMenu("Editor Zoom")','menu.addMenu("Editor Miscellaneous")'):
    assert required in view,required
for required in ('menu.addMenu("App Theme")','menu.addMenu("App Icons")','menu.addMenu("App Drag-and-Drop")','menu.addMenu("Duplicate File with Unsaved Changes")','menu.addMenu("Open Externally with Unsaved Changes")'):
    assert required in settings,required
assert 'Focused Mode' not in source
# Ribbon structure retains shared Home/Insert organization and approved Configure groups.
home=ribbon[ribbon.index('home=page("Home")'):ribbon.index('insert_page=page("Insert")')]
insert=ribbon[ribbon.index('insert_page=page("Insert")'):ribbon.index('view=page("Configure")')]
configure=ribbon[ribbon.index('view=page("Configure")'):ribbon.index('help_page=page("Help")')]
assert 'group(home,"Advanced")' not in home
for needle in ('group(insert_page,"Advanced")','cab(g,"find",0,0)','cab(g,"replace",0,1)','cab(g,"duplicate-line",1,0)','cab(g,"delete-line",1,1)'):
    assert needle in insert,needle
for group in ('View Control','Editor Settings','Theme Settings','App Settings'):
    assert f'group(view,"{group}")' in configure
# Generic shell behavior retained.
assert '"Disable Locked Mode? — RiqatonyPad"' in lock
assert 'QCheckBox("Don\'t ask again when disabling Locked Mode"' in lock
assert 'suffix=" — Locked Mode" if self.view_only else ""' in title
assert 'folder=parent.name or str(parent)' in title
assert 'self.setWindowTitle(f"{prefix}{name}{scope} — RiqatonyPad{suffix}")' in title
assert 'Col:' not in status and 'positionInBlock' not in status
assert 'Chars {characters:,}' in status and 'Zoom:' not in status
assert '"Words",count_words(text)' in props and '"Full path",path' in props and '"Location",os.path.dirname(path)' in props
for plus_only in ('Focused Mode','Show Dashboard','File Header','Previous File','Next File'):
    assert plus_only not in source,plus_only
print('PASS: RiqatonyPad 1.0.4 shared shell behavior retained with approved standalone UI selector placement')
