#!/usr/bin/env python3
"""x16.3: strict supplied-pack inventories, command/icon wiring, theme refresh and scope."""
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
assert 'APP_VERSION = "2.0.0-x16.3"' in APP.read_text(encoding='utf-8')
print('PASS: x16.3 exact supplied inventory, four Pad icon bindings, preserved radio/theme behavior')
