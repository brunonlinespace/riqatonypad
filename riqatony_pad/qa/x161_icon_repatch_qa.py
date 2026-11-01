#!/usr/bin/env python3
"""x161 source-bound supplied-icon provenance and exact approved action binding gate."""
from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[1]
reference=json.loads((ROOT/'qa/x161_icon_provenance.json').read_text(encoding='utf-8'))
assert set(reference)=={'ribbon-icons','ribbon-icons-classic','ribbon-icons-original'}
for family,items in reference.items():
    assert len(items)==288,(family,len(items))
    for rel,expected in items.items():
        path=ROOT/'assets'/family/rel
        data=path.read_bytes()
        assert hashlib.sha256(data).hexdigest()==expected,(family,rel)
        assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(64,64),(family,rel)
    for mode in ('light','dark'):
        names={p.stem for p in (ROOT/'assets'/family/mode).glob('*.png')}
        assert {'find','heading-group','link-group','icons-legacy','icons-new','icons-classic','dirty-duplicate-policy','dirty-external-policy',*(f'heading-{n}' for n in range(7))} <= names,(family,mode)
editor=(ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
for label in ('Riqa Icons Harmony','Riqa Icons Humility','Riqa Icons Heritage'):
    assert label in editor,label
for forbidden in ('"Rico Icons Harmony"','"Rico Icons Classic"','"Rico Icons Legacy"'):
    assert forbidden not in editor,forbidden
assert 'self.bind_custom_icon(link_menu.menuAction(),"link-group")' in editor
assert 'self.bind_custom_icon(heading_menu.menuAction(),"heading-group")' in editor
assert 'self.bind_custom_icon(action,f"heading-{level}")' in editor
assert '"new"' in editor and '"classic"' in editor and '"original"' in editor
for token in ('("Advanced", "find", "Find", "action", "search_bar_action", "find")','"icon_original_action", "icons-legacy"','"dirty_duplicate_menu", "dirty-duplicate-policy"','"dirty_external_menu", "dirty-external-policy"'):
    assert token in editor,token
assert '"new":"Harmony","classic":"Humility","original":"Heritage"' in editor
assert 'self.appimage_icon_set = "new"' in (ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
assert 'APP_VERSION = "2.0.0-x16.1"' in (ROOT/'app.py').read_text(encoding='utf-8')
# Explicit exclusion: this release must not remap the toolbar-layout icons.
assert '"toolbar-tabbed"' not in editor and '"toolbar-classic"' not in editor
print('PASS: supplied family bytes, exact icon wiring, labels and deferred toolbar-layout icons')
