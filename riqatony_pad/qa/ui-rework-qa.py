#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.4 Configure/AppMenu cosmetic rework gate."""
from pathlib import Path
import ast
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
source=contract_text(ROOT)
source += '\n' + (ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
ribbon_source=(ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
ribbon_tree=ast.parse(ribbon_source)
ribbon_cls=next(n for n in ribbon_tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorRibbonRetroMixin')
ribbon_methods={n.name:n for n in ribbon_cls.body if isinstance(n,ast.FunctionDef)}
module=ast.parse(source)
cls=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
_commands_mixin=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='EditorCommandsAppearanceMixin')
_commands_methods={n.name:n for n in _commands_mixin.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(_commands_methods)
methods.update(_commands_methods)
def seg(name): return (ast.get_source_segment(ribbon_source,ribbon_methods[name]) or '') if name in ribbon_methods else (ast.get_source_segment(source,methods[name]) or '')
view=seg('make_view_menu'); settings=seg('make_settings_menu'); ribbon=seg('build_ribbon'); icon=seg('custom_icon'); dark=seg('update_editor_canvas_theme_action')
# AppMenu View exact approved structure.
for needle in ('menu.addMenu("Editor Layout")','menu.addMenu("Editor Toolbar")','menu.addMenu("Editor Zoom")','menu.addMenu("Editor Miscellaneous")'):
    assert needle in view, needle
assert view.index('"Full Screen"') < view.index('"Show Status"') < view.index('"Word Wrap"') < view.index('"Dark Editor"') < view.index('"Locked Mode"') < view.index('menu.addMenu("Editor Layout")') < view.index('menu.addMenu("Editor Toolbar")') < view.index('menu.addMenu("Editor Zoom")') < view.index('menu.addMenu("Editor Miscellaneous")')
# Settings exact approved structure and labels.
for needle in ('menu.addMenu("App Theme")','menu.addMenu("App Icons")','menu.addMenu("App Drag-and-Drop")','menu.addMenu("Duplicate File with Unsaved Changes")','menu.addMenu("Open Externally with Unsaved Changes")'):
    assert needle in settings, needle
assert 'menu.addMenu("File Handling")' not in settings
assert settings.index('menu.addMenu("App Theme")') < settings.index('menu.addMenu("App Icons")') < settings.index('menu.addMenu("App Drag-and-Drop")') < settings.index('menu.addMenu("Duplicate File with Unsaved Changes")') < settings.index('menu.addMenu("Open Externally with Unsaved Changes")')
# Configure Ribbon exact requested two-row layout, including swapped App Settings rows.
configure=ribbon[ribbon.index('view=page("Configure")'):ribbon.index('help_page=page("Help")')]
for needle in (
    'cab(g,"full-screen",0,0)', 'cab(g,"status-bar",0,1)', 'cmb(g,"editor-layout",0,2)',
    'cab(g,"zoom-out",1,0)', 'cab(g,"zoom-reset",1,1)', 'cab(g,"zoom-in",1,2)',
    'cmb(g,"editor-toolbar",0,0)', 'cab(g,"tab-width",0,1)', 'cab(g,"default-font",0,2)',
    'cab(g,"word-wrap",1,0)', 'cab(g,"editor-canvas",1,1)', 'cab(g,"view-only",1,2)',
    'cab(g,"icons-new",0,0)', 'cab(g,"icons-classic",0,1)', 'cab(g,"icons-original",0,2)',
    'cab(g,"theme-light",1,0)', 'cab(g,"theme-dark",1,1)', 'cab(g,"theme-system",1,2)',
    'cab(g,"drop-new-window",0,0)', 'cmb(g,"dirty-external",0,1)',
    'cab(g,"drop-active",1,0)', 'cmb(g,"dirty-duplicate",1,1)',
): assert needle in configure, needle
# Top-level submenu icons resolve from the same shared command registry.
for item_id in ('editor-layout','editor-toolbar','app-theme','app-icons','app-drag-drop','dirty-duplicate','dirty-external'):
    assert f'"{item_id}"' in configure
assert 'for item_id in ("editor-layout","editor-toolbar","app-theme","app-icons","app-drag-drop","dirty-duplicate","dirty-external"):' in configure
for forbidden in ('resource_path("riqatonypad-icons"','"layout-retro"'):
    assert forbidden not in configure+icon, forbidden
assert not (ROOT/'assets'/'riqatonypad-icons').exists()
# Dark Editor tooltip remains the exact Plus explanatory wording.
assert 'the ribbon and the rest of the interface will not change.' in dark
print('PASS: RiqatonyPad 1.0.4 approved Configure/AppMenu rework and 106-family-only asset contract')
