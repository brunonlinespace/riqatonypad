#!/usr/bin/env python3
"""x16.5: retained strict supplied-pack inventories, command/icon wiring, theme refresh and scope."""
from pathlib import Path
from hashlib import sha256
from struct import unpack
import ast
import json
ROOT = Path(__file__).resolve().parents[1]
APP = ROOT/'app.py'
editor_path = ROOT/'widgets/editor_commands_appearance.py'
editor = editor_path.read_text(encoding='utf-8')
ribbon = (ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
originals = json.loads((ROOT/'qa/x161_icon_provenance.json').read_text(encoding='utf-8'))
patch = {
    'dark/external-editor.png': 'f1813b2e7dcb5ac9fb59abab187cf8658fccff307bc8ab5fdc81c3ee124177f4',
    'dark/launch-last-file.png': '4f188dc67d2fe22ace83b768bf66fbdfdc381821f7a3945a6acd740cf5f31aa0',
    'light/external-editor.png': '6eb5fe3025d38b31494e072904b58f96a92c005d456ed24f09db98afca2cefb4',
    'light/launch-last-file.png': '9c8b2b60b1851e2686a1d292c0a391f46ecbbc58e6489bec3d5b68a7d097db99',
}
for family, source_hashes in originals.items():
    base = ROOT/'assets'/family
    # The x16.1 provenance records all 144 originals + surplus retained icons;
    # x16.3 must ship EXACTLY the 144 names common to the supplied packs.
    excludes = {'search-toggle.png'}
    if family == 'ribbon-icons':
        excludes.update({'dark-mode.png', 'light-theme.png', 'system-theme.png',
                         'markdown-source.png', 'open-external-file.png', 'paste-markdown.png'})
    expected = {rel: (patch[rel] if family == 'ribbon-icons-original' and rel in patch else digest)
                for rel, digest in source_hashes.items()
                if Path(rel).name not in excludes}
    actual = {p.relative_to(base).as_posix():p for p in base.rglob('*') if p.is_file()}
    assert set(actual) == set(expected), (family,sorted(set(actual)-set(expected)),sorted(set(expected)-set(actual)))
    assert len(expected) == 288, (family,len(expected))
    for rel, p in actual.items():
        contents = p.read_bytes()
        assert p.suffix == '.png' and contents[:8] == b'\x89PNG\r\n\x1a\n'
        assert unpack('>II',contents[16:24]) == (64,64)
        assert sha256(contents).hexdigest() == expected[rel],(family,rel)
    dark = {p.name for p in (base/'dark').glob('*.png')}
    light = {p.name for p in (base/'light').glob('*.png')}
    assert dark == light and len(dark) == 144
    for icon in ('app-drag-and-drop','layout','toolbar-tabbed','toolbar-classic'):
        assert f'{icon}.png' in dark,(family,icon)
# The same shared catalog feeds both the Ribbon presentation and Retro customization.
tree = ast.parse(editor)
specs = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign)
             and any(isinstance(target,ast.Name) and target.id=='COMMAND_SURFACE_SPECS' for target in node.targets))
by_id = {row[1]:row for row in specs}
assert by_id['app-drag-drop'][-1] == 'app-drag-and-drop'
assert by_id['editor-layout'][-1] == 'layout'
assert by_id['editor-toolbar'][-1] == 'layout-ribbon'  # untouched group icon
assert 'self.bind_custom_icon(action,"toolbar-tabbed" if mode=="ribbon" else "toolbar-classic")' in editor
assert 'menu.menuAction().setIcon(self.custom_icon("app-drag-and-drop"))' in editor
assert 'menu.menuAction().setIcon(selected.icon())' not in editor
assert 'self._sync_app_drag_drop_menu_icon()' in editor
assert 'self._sync_app_drag_drop_menu_icon()' in (ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
assert 'self._sync_app_drag_drop_menu_icon()' in APP.read_text(encoding='utf-8')
assert 'self.bind_custom_icon(getattr(self,attr).menuAction(),icon)' in ribbon
assert 'return self.command_surface_catalog()' in editor
assert 'self.layout_actions["ribbon"]' in ribbon and 'self.layout_actions["retro"]' in ribbon
assert 'action.setChecked(mode == style)' in ribbon
assert 'self.bind_custom_icon(b,icon)' in ribbon and 'self.bind_custom_icon(action,icon)' in ribbon
assert 'for target, icon_name in tuple(self.icon_bindings):' in editor  # refreshed on theme/family change
assert 'APP_VERSION = "2.0.0"' in APP.read_text(encoding='utf-8')
print('PASS: x16.5 retained exact icon inventory and Pad icon bindings')


# Execute the genuine module and wizard function, not just source text greps.
# A missing imported name was the x16.3 failure; this test catches that error
# even on machines where PyQt6 itself is not installed.
import hashlib
import importlib.util
import sys
from types import ModuleType
from unittest.mock import MagicMock

TOUR = ROOT/'widgets/quick_tour.py'
text = TOUR.read_text(encoding='utf-8')
tree = ast.parse(text)
func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'show_tutorial_wizard')
assert hashlib.sha256(ast.dump(func, include_attributes=False).encode()).hexdigest() == '669f324e6a0f8ad21dab14686e4af2f74f3860f9da4afa20e127e76b42de39fb', \
    'Out-of-scope Quick Tour page content or callbacks changed'
qt_imports = {node.module: {alias.name for alias in node.names}
              for node in tree.body if isinstance(node, ast.ImportFrom)}
assert {'Qt', 'QTimer'} <= qt_imports['PyQt6.QtCore']
assert {'QCheckBox', 'QLabel', 'QPushButton', 'QVBoxLayout', 'QWizard', 'QWizardPage'} <= qt_imports['PyQt6.QtWidgets']

qt = ModuleType('PyQt6')
core = ModuleType('PyQt6.QtCore')
widgets = ModuleType('PyQt6.QtWidgets')
qt.__path__ = []
core.Qt = MagicMock(name='Qt')
core.QTimer = MagicMock(name='QTimer')
for name in ('QCheckBox','QLabel','QPushButton','QVBoxLayout','QWizard','QWizardPage'):
    setattr(widgets, name, MagicMock(name=name))
keys = ('PyQt6', 'PyQt6.QtCore', 'PyQt6.QtWidgets')
saved = {key: sys.modules.get(key) for key in keys}
try:
    sys.modules.update({'PyQt6':qt, 'PyQt6.QtCore':core, 'PyQt6.QtWidgets':widgets})
    spec = importlib.util.spec_from_file_location('riqa_x164_quick_tour_test', TOUR)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
finally:
    for key, original in saved.items():
        if original is None:
            sys.modules.pop(key, None)
        else:
            sys.modules[key] = original

class FakeHost:
    tutorial_dialog = None
    tutorial_seen = False
    def __init__(self):
        self.save_preferences = MagicMock(name='save_preferences')
        self.show_keyboard_shortcuts_dialog = MagicMock(name='show_keyboard_shortcuts_dialog')
        self._focus_editor_after_startup = MagicMock(name='_focus_editor_after_startup')
    def windowIcon(self):
        return None

host = FakeHost()
mod.show_tutorial_wizard(host)  # x16.3 would raise NameError: QWizardPage
wizard = widgets.QWizard.return_value
assert host.tutorial_dialog is wizard
assert widgets.QWizardPage.call_count == 7
assert widgets.QLabel.call_count == 7
assert wizard.addPage.call_count == 7
assert widgets.QPushButton.return_value.clicked.connect.call_args.args[0] == host.show_keyboard_shortcuts_dialog
checkbox = widgets.QCheckBox.return_value
checkbox.toggled.connect.call_args.args[0](True)
assert host.tutorial_seen is True
host.save_preferences.assert_called_once_with()
mod.show_tutorial_wizard(host)
assert widgets.QWizard.call_count == 1, 'Reopening an active tour must not create another wizard'
assert wizard.show.call_count == 2
wizard.finished.connect.call_args.args[0](0)
assert host.tutorial_dialog is None
core.QTimer.singleShot.assert_called_once_with(0, host._focus_editor_after_startup)
print('PASS: x16.4 Quick Tour seven pages, startup option, shortcuts, re-show, and close callback')
