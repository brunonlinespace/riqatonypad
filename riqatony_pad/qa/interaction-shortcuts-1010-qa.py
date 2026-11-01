#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.10 bounded interaction/shortcut gate."""
from pathlib import Path
import ast, hashlib
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
req('APP_VERSION = "1.0.10"' in source,'1.0.10 identity missing')
tree=ast.parse(source)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
def body(name):
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    return ast.get_source_segment(source,fn) or ''
highlight=body('choose_highlight_colour')
for fragment in (
    '("Yellow", "#fff200", "Y")', '("Pink", "#ff99cc", "P")',
    '("Green", "#92d050", "G")', '("Red", "#ff6666", "R")',
    '("Blue", "#5b9bd5", "B")', '("Orange", "#f4b183", "O")',
    '("Cyan", "#66ffff", "C")', '("Noir", "#000000", "N")',
    'shortcut.setShortcut(QKeySequence(key))',
    'shortcut.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)',
    'shortcut.triggered.connect(lambda _checked=False,value=hex_colour:choose(value))',
    'clear_shortcut.setShortcut(QKeySequence("Backspace"))',
    'clear_shortcut.triggered.connect(clear)',
    'chosen["colour"]=QColor(hex_colour); dialog.accept()',
    'chosen["clear"]=True; dialog.accept()',
): req(fragment in highlight,f'highlight interaction missing: {fragment}')
req('("Black", "#000000"' not in highlight,'highlight Black label was not replaced by Noir')
view=body('make_view_menu'); settings=body('make_settings_menu'); fmt=body('make_format_menu'); colour=body('choose_text_colour')
for mode,label,key in (
    (1,'Toolbar + Find — Top','Ctrl+1'),(2,'Toolbar + Find — Bottom','Ctrl+2'),
    (3,'Toolbar — Top / Find — Bottom','Ctrl+3'),(4,'Toolbar — Bottom / Find — Top','Ctrl+4'),
): req(f'({mode},"{label}","{key}")' in view,f'Editor Layout shortcut missing: {key}')
req('QKeySequence("Ctrl+Alt+Shift+T")' in view,'Ribbon/Retro toggle shortcut missing')
req('self.set_interface_style("retro" if self.interface_style=="ribbon" else "ribbon")' in view,'Ribbon/Retro toggle does not use existing interface setter')
req('("ribbon","Ribbon (default)","Ctrl+Alt+Shift+1")' not in view,'old Ribbon shortcut remains')
req('("retro","Retro","Ctrl+Alt+Shift+2")' not in view,'old Retro shortcut remains')
for theme,label,key in (
    ('light','Light','Ctrl+Alt+Shift+1'),('dark','Dark','Ctrl+Alt+Shift+2'),('system','System','Ctrl+Alt+Shift+3'),
): req(f'("{theme}","{label}","{key}")' in settings,f'App Theme shortcut missing: {key}')
for key in ('Ctrl+1','Ctrl+2','Ctrl+3','Ctrl+4'):
    req(key not in fmt,f'Line Spacing still owns {key}')
req('Clear Colour' not in colour and 'clear_colour' not in colour,'Clear Colour was added despite explicit exclusion')
protected={
 'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8',
 'rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb',
 'rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41',
 'widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310',
}
for r,h in protected.items(): req(sha(r)==h,f'protected out-of-scope file changed: {r}')
if errors:
    print('RiqatonyPad 1.0.10 interaction/shortcut check failed:')
    [print('- '+e) for e in errors]
    raise SystemExit(1)
print('PASS: RiqatonyPad 1.0.10 bounded interaction/shortcut contract')
