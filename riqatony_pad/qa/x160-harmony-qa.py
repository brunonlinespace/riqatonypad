#!/usr/bin/env python3
"""RiqatonyPad x16.0 Harmony default: immutable references and bounded source diff."""
from pathlib import Path
import hashlib,json,ast,re,struct
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'qa/x160-predecessor-integrity.json').read_text(encoding='utf-8'))
assert DATA['predecessor']=='2.0.0-x13.5' and DATA['release']=='2.0.0-x16.0'
for rel,digest in DATA['untouched_files'].items():
    f=ROOT/rel
    assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest,rel
for rel,digest in DATA['preserved_nondefault_pngs'].items():
    f=ROOT/rel
    assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest,rel
assert len(DATA['harmony_pngs'])==296
for rel,digest in DATA['harmony_pngs'].items():
    f=ROOT/'assets/ribbon-icons'/rel
    assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest,rel
    data=f.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(64,64),rel
found={f.relative_to(ROOT/'assets/ribbon-icons').as_posix() for f in (ROOT/'assets/ribbon-icons').rglob('*') if f.is_file()}
assert found==set(DATA['harmony_pngs']),(sorted(found-set(DATA['harmony_pngs'])),sorted(set(DATA['harmony_pngs'])-found))
assert not list(ROOT.rglob('*.svg'))
assert not any((ROOT/'tools'/n).exists() for n in ('generate-ribbon-icons.py','generate-classic-ribbon-icons.py'))
assert len(list(ROOT.rglob('*.png')))==742
assert len(DATA['preserved_nondefault_pngs'])==446
for variant in ('light','dark'):
    harmony={f.stem for f in (ROOT/'assets/ribbon-icons'/variant).glob('*.png')}
    legacy={f.stem for f in (ROOT/'assets/ribbon-icons-original'/variant).glob('*.png')}
    classic={f.stem for f in (ROOT/'assets/ribbon-icons-classic'/variant).glob('*.png')}
    assert len(harmony)==148 and len(legacy)==len(classic)==106
    assert classic<=harmony and legacy<=harmony
source=(ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
preferences=(ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
assert 'Rico Icons Harmony' in source and 'Rico Icons Modern' not in source
assert 'label={"new":"Harmony","classic":"Classic","original":"Legacy"}[icon_set]' in source
assert 'self.appimage_icon_set = "new"' in preferences
assert 'saved_icon_set in ("new", "classic", "original")' in preferences
assert '"classic": "ribbon-icons-classic"' in source
assert '"original": "ribbon-icons-original"' in source
assert 'APP_VERSION = "2.0.0-x16.0"' in (ROOT/'app.py').read_text(encoding='utf-8')
print('PASS: x16.0 exactly supplied Harmony PNGs, all nondefault PNGs preserved, stable preference and scope')
