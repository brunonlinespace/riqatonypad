#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.1.2 App Drag-and-Drop parent icon synchronization gate."""
from __future__ import annotations
import ast, hashlib
from pathlib import Path
from source_contract import contract_text
from shortcut_legacy import legacy_read_bytes
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def req(c,m):
    if not c: errors.append(m)
def sha(rel):
    data=legacy_read_bytes(ROOT, rel)
    if rel in ("rtf_new_document.py", "widgets/shortcut_search.py"):
        assert data.startswith(b"#!/usr/bin/env python3\n"), f"x12.2 approved shebang missing: {rel}"
        data=data[len(b"#!/usr/bin/env python3\n"):]
    return hashlib.sha256(data).hexdigest()
source=contract_text(ROOT)
source += '\n' + (ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
req('APP_VERSION = "2.0.0-x13.0"' in source,'1.1.2 identity missing')
req('self.app_drag_drop_menu=menu.addMenu("App Drag-and-Drop")' in source,'App Drag-and-Drop menu label changed')
req('("active_window","Opens on Active Window")' in source and '("new_window","Opens on New Window")' in source,'drag/drop radio labels changed')
tree=ast.parse(source); cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
pref_source=(ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
pref_cls=next(n for n in ast.parse(pref_source).body if isinstance(n,ast.ClassDef) and n.name=='EditorPreferencesMixin')
command_cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorCommandsAppearanceMixin')
def fn(name):
    for owner in (cls,pref_cls,command_cls):
        for n in owner.body:
            if isinstance(n,ast.FunctionDef) and n.name==name:return n
    raise KeyError(name)
def segment(name):
    return ast.get_source_segment(pref_source if name=='apply_preferences' else source,fn(name)) or ''
sync=ast.get_source_segment(source,fn('_sync_app_drag_drop_menu_icon')) or ''
req('getattr(self, "drop_behaviour_actions", {}).get(self.drop_open_mode)' in sync,'parent icon is not selected from authoritative drag/drop mode')
req('menu.menuAction().setIcon(selected.icon())' in sync,'AppMenu parent does not mirror selected radio icon')
for name in ('apply_preferences','set_drop_open_mode','refresh_portable_icons'):
    seg=segment(name)
    req('self._sync_app_drag_drop_menu_icon()' in seg,f'{name} does not resynchronize App Drag-and-Drop parent icon')
setmode=ast.get_source_segment(source,fn('set_drop_open_mode')) or ''
req('self.drop_open_mode = mode' in setmode and 'self.save_preferences()' in setmode,'drag/drop behavior/persistence path changed')
# Selected radio assets remain available in every family/scheme.
for family in ('ribbon-icons','ribbon-icons-classic','ribbon-icons-original'):
    for scheme in ('light','dark'):
        for name in ('drop-active.png','drop-new-window.png'):
            req((ROOT/'assets'/family/scheme/name).is_file(),f'missing drag/drop icon asset: {family}/{scheme}/{name}')
# Exact bounded runtime file plus precious format/support modules.
# x3.0 relocates existing editor methods; the baseline-pinned AST check replaces
# the obsolete whole-file hash, without weakening the method-body contract.
import runpy
runpy.run_path(str(ROOT / 'qa/x3-insertion-extraction-qa.py'), run_name='__main__')
protected={
 'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8',
 'rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb',
 'rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41',
 'widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310',
}
for rel,h in protected.items(): req(sha(rel)==h,f'protected out-of-scope file changed: {rel}')
if errors:
    print('RiqatonyPad 1.1.2 check failed:')
    [print('- '+e) for e in errors]
    raise SystemExit(1)
print('PASS: RiqatonyPad 1.1.2 bounded App Drag-and-Drop parent icon synchronization contract')
