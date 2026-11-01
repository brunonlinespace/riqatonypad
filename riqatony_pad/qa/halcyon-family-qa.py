#!/usr/bin/env python3
"""Edition 2.0.0-x16.5 Halcyon artwork and selection contract."""
from pathlib import Path
import zipfile, hashlib
root=Path(__file__).resolve().parents[1]
outer=root.parent
scheme_set={'dark','light'}
assets=root/'assets'/'ribbon-icons-aero'
assert {p.name for p in assets.iterdir()} == scheme_set
for scheme in scheme_set:
    members=list((assets/scheme).glob('*.png'))
    assert len(members)==144,(scheme,len(members))
    assert (assets/scheme/'app-icons.png').is_file()
source=(root/'widgets/editor_commands_appearance.py').read_text()
assert '("aero","Riqa Icons Halcyon")' in source
assert '"aero": "ribbon-icons-aero"' in source
assert '"aero"' in source
app=(root/'app.py').read_text()
prefs=(root/'widgets/rwpyn/editor_preferences.py').read_text()
assert '("new", "classic", "original", "aero")' in app
assert '("new", "classic", "original", "aero")' in prefs
assert '"aero":"Halcyon"' in source
ribbon=(root/'widgets/editor_ribbon_retro.py').read_text()
assert 'icons-aero' not in ribbon and 'icon_aero_action' not in ribbon
print('PASS Halcyon fourth AppMenu-only family and artwork inventory')

builder=(root/'packaging/fedora/build-appimage.sh').read_text()
for expected in ('AERO_RIBBON_ICON_DIR=', '${AERO_RIBBON_ICON_DIR}/light',
                 '${AERO_RIBBON_ICON_DIR}/dark',
                 '${SOURCE_STAGE}/ribbon-icons-aero/light',
                 '${SOURCE_STAGE}/ribbon-icons-aero/dark',
                 '--add-data "${SOURCE_STAGE}/ribbon-icons-aero:ribbon-icons-aero"'):
    assert expected in builder,expected
print('PASS Halcyon included in frozen AppImage source payload')
