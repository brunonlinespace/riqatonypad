#!/usr/bin/env python3
"""RiqatonyPad 1.0.3 approved standalone UI-cleanup gate."""
from pathlib import Path
import ast
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
source=contract_text(ROOT)
source += '\n' + (ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
module=ast.parse(source)
cls=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
_commands_mixin=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='EditorCommandsAppearanceMixin')
_commands_methods={n.name:n for n in _commands_mixin.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(_commands_methods)
methods.update(_commands_methods)
prefs_source=(ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
ribbon_source=(ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
ribbon_cls=next(n for n in ast.parse(ribbon_source).body if isinstance(n,ast.ClassDef) and n.name=='EditorRibbonRetroMixin')
ribbon_methods={n.name:n for n in ribbon_cls.body if isinstance(n,ast.FunctionDef)}
prefs_cls=next(n for n in ast.parse(prefs_source).body if isinstance(n,ast.ClassDef) and n.name=='EditorPreferencesMixin')
prefs_methods={n.name:n for n in prefs_cls.body if isinstance(n,ast.FunctionDef)}
def seg(name): return (ast.get_source_segment(prefs_source,prefs_methods[name]) if name in prefs_methods else ast.get_source_segment(ribbon_source,ribbon_methods[name]) if name in ribbon_methods else ast.get_source_segment(source,methods[name])) or '' 
file_menu=seg('make_file_menu'); edit=seg('make_edit_menu'); view=seg('make_view_menu'); settings=seg('make_settings_menu'); docs=seg('open_documentation'); new_window=seg('new_window'); collapse=seg('set_ribbon_collapsed'); save_prefs=seg('save_preferences'); tip=seg('_toolbar_action_tooltip')
# File: Save As immediately followed by More Actions; exact Plus submenu order/wording.
assert 'self.save_as_action = self.add_menu_action(menu, "Save As…", self.save_as_file, QKeySequence.StandardKey.SaveAs)\n        self.more_actions_menu = menu.addMenu("More Actions")' in file_menu
order=('"Duplicate File…"','"Rename File…"','"Delete File"','"Open in External Editor"','"Open Containing Folder"','"Properties"')
pos=[file_menu.index(x) for x in order]; assert pos==sorted(pos),pos
assert file_menu.count('self.more_actions_menu.addSeparator()')==2
# Edit labels only; unified behavior remains connected.
assert 'QAction("Find",self)' in edit and 'menu,"Find and Replace"' in edit
assert 'Find Bar' not in edit and 'Find and Replace…' not in edit
# Exact approved View ordering.
order=('"Full Screen"','"Show Status"','"Word Wrap"','"Dark Editor"','"Locked Mode"','menu.addMenu("Editor Layout")','menu.addMenu("Editor Toolbar")','menu.addMenu("Editor Zoom")','menu.addMenu("Editor Miscellaneous")')
pos=[view.index(x) for x in order]; assert pos==sorted(pos),pos
for label in ('Toolbar Top / Find Bottom','Toolbar Top / Find Top','Toolbar Bottom / Find Top','Toolbar Bottom / Find Bottom'):
    assert label in view
# Two requested separator boundaries before Word Wrap and before Locked Mode, plus one before zoom/misc group.
assert view.count('\n        menu.addSeparator()')==3
# Toolbar tooltip overrides: Theme and Drag-and-Drop only; icon family wording remains unchanged.
assert 'for theme,label in (("light","Light"),("dark","Dark"),("system","System")):' in settings
assert 'action.setProperty("riqatonypad_toolbar_tooltip",f"Theme — {label}")' in settings
assert 'for mode,label in (("active_window","Opens on Active Window"),("new_window","Opens on New Window")):' in settings
assert 'action.setProperty("riqatonypad_toolbar_tooltip",f"Drag-and-Drop — {label}")' in settings
assert 'riqatonypad_toolbar_tooltip' in tip
assert 'Icons —' not in settings
# Documentation: construct hidden, lock, transiently collapse only Ribbon, then show.
assert 'self.new_window(str(path), show=False)' in docs
assert 'window.view_only = True' in docs
assert 'if window.interface_style == "ribbon":' in docs and 'window.set_ribbon_collapsed(True, persist=False)' in docs
assert docs.index('window.set_ribbon_collapsed(True, persist=False)') < docs.index('window.show()')
assert 'def new_window(self, file_path=None, *, show=True):' in new_window
assert 'if show:' in new_window
# persist=False must truly leave the saved collapse preference alone.
assert 'if persist:\n            self.ribbon_collapsed_preference = collapsed' in collapse
assert '"ribbon_collapsed": bool(self.ribbon_collapsed_preference)' in save_prefs
print('PASS: RiqatonyPad 1.0.3 approved AppMenu/tooltips/Documentation cleanup')
