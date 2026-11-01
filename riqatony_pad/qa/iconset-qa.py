#!/usr/bin/env python3
"""Audit x16.3 exact supplied Harmony/Humility/Heritage command icon inventories."""
from pathlib import Path
import ast, hashlib, re, struct
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
SOURCE=contract_text(ROOT)
SOURCE+=(ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
PREFERENCES=(ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
TREE=ast.parse(SOURCE)
required=set()
for node in TREE.body:
    if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='COMMAND_SURFACE_SPECS':
        for row in ast.literal_eval(node.value):
            if row[-1]: required.add(row[-1])
        break
else:
    raise AssertionError('COMMAND_SURFACE_SPECS missing')
for m in re.finditer(r'\b(?:ab|fb|mb)\([^\n]*?["\']([a-z0-9-]+)["\']\s*(?:,|\))',SOURCE):
    required.add(m.group(1))
for m in re.finditer(r'bind_custom_icon\([^,]+,\s*["\']([a-z0-9-]+)["\']',SOURCE):
    required.add(m.group(1))
required.update({'layout','toolbar-tabbed','toolbar-classic','app-drag-and-drop','app-theme','app-icons','duplicate-file','external-editor'})
assert 'layout-retro' not in required, sorted(required)
assert 'riqatonypad-icons' not in SOURCE
assert not (ROOT/'assets'/'riqatonypad-icons').exists()

families={
    'new': ROOT/'assets'/'ribbon-icons',
    'classic': ROOT/'assets'/'ribbon-icons-classic',
    'original': ROOT/'assets'/'ribbon-icons-original',
}
expected_aggregate={
    'new':'ca4adb01d1e436594407746049f00a5c1a2e69d6941813e286628c727b54485e',
    'classic':'c61fb317c2c77817037d10c745693df2b88ff8af8d100960d528f2d8000a2b92',
    'original':'bff6678ccc8948d863bd0375c15cf255510b547b4c4c8a2667aa8c033eb99026',
}
def aggregate(base: Path) -> str:
    h=hashlib.sha256()
    for p in sorted(base.rglob('*.png')):
        h.update(p.relative_to(base).as_posix().encode()); h.update(b'\0'); h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()
reference=None
for family,base in families.items():
    assert aggregate(base)==expected_aggregate[family], (family,aggregate(base))
    for variant in ('light','dark'):
        png_dir=base/variant
        pngs={p.stem for p in png_dir.glob('*.png')}
        assert len(pngs)==144,(family,variant,len(pngs))
        assert required <= pngs,(family,variant,sorted(required-pngs))
        if family == "new":
            if reference is None: reference = pngs
            else: assert pngs == reference,(family,variant,"Harmony theme inventories differ")
        else:
            assert required <= pngs,(family,variant,"Missing command icons",sorted(required-pngs))
        for name in sorted(pngs):
            data=(png_dir/f'{name}.png').read_bytes(); assert data[:8]==b'\x89PNG\r\n\x1a\n'
            w,h=struct.unpack('>II',data[16:24]); assert (w,h)==(64,64),(family,variant,name,w,h)
assert 'for icon_set,label in (("new","Riqa Icons Harmony"),("classic","Riqa Icons Humility"),("original","Riqa Icons Heritage"),("aero","Riqa Icons Halcyon")):' in SOURCE
assert 'requested_icon_set in ("new", "classic", "original", "aero")' in SOURCE
assert 'saved_icon_set in ("new", "classic", "original", "aero")' in PREFERENCES
assert 'if icon_set not in ("new","classic","original","aero")' in SOURCE
assert '"original": "ribbon-icons-original"' in SOURCE
print('PASS: Harmony/Humility/Heritage exact supplied light/dark icon inventories, no SVG, complete command coverage')
