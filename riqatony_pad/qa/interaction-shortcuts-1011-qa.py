#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.11 shortcut/layout refinement gate."""
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
def fhash(text, cls_name, name):
    tree=ast.parse(text); cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls_name)
    fn=next((n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name),None)
    if fn is None:
        for filename,classname in (('widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin'),('widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin'),('widgets/rwpyn/editor_formatting.py','EditorFormattingMixin')):
            candidate=(ROOT/filename).read_text(encoding='utf-8')
            candidate_cls=next(n for n in ast.parse(candidate).body if isinstance(n,ast.ClassDef) and n.name==classname)
            fn=next((n for n in candidate_cls.body if isinstance(n,ast.FunctionDef) and n.name==name),None)
            if fn is not None:
                text=candidate
                break
        if fn is None: raise AssertionError(f'Missing preserved method: {name}')
    seg=ast.get_source_segment(text,fn) or ''
    return hashlib.sha256(seg.encode()).hexdigest(), seg
source=contract_text(ROOT)
source += '\n' + (ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
ribbon_source=(ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
preferences=(ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
req('APP_VERSION = "2.0.0-x13.0"' in source,'1.0.11 identity missing')
_,highlight=fhash(source,'RiqatonyPad','choose_highlight_colour')
for fragment in (
    '("Yellow", "#fff200", "Y")','("Pink", "#ff99cc", "P")','("Green", "#92d050", "G")','("Red", "#ff6666", "R")',
    '("Blue", "#5b9bd5", "B")','("Orange", "#f4b183", "O")','("Cyan", "#66ffff", "C")','("Noir", "#000000", "N")',
    'button=QPushButton(f"{name} ({key})",dialog)','clear_button=QPushButton("Clear Highlight (Backspace)",dialog)',
    'shortcut.triggered.connect(lambda _checked=False,value=hex_colour:choose(value))','clear_shortcut.triggered.connect(clear)',
    'chosen["colour"]=QColor(hex_colour); dialog.accept()','chosen["clear"]=True; dialog.accept()',
): req(fragment in highlight,f'highlight contract missing: {fragment}')
req('QPushButton(name,dialog)' not in highlight,'highlight labels do not expose keybinds')
_,view=fhash(source,'RiqatonyPad','make_view_menu'); _,settings=fhash(source,'RiqatonyPad','make_settings_menu'); _,fmt=fhash(source,'RiqatonyPad','make_format_menu'); _,colour=fhash(source,'RiqatonyPad','choose_text_colour')
expected=(
    (3,'Toolbar Top / Find Bottom','Ctrl+Alt+Shift+1'),
    (1,'Toolbar Top / Find Top','Ctrl+Alt+Shift+2'),
    (4,'Toolbar Bottom / Find Top','Ctrl+Alt+Shift+3'),
    (2,'Toolbar Bottom / Find Bottom','Ctrl+Alt+Shift+4'),
)
for mode,label,key in expected:
    req(f'({mode},"{label}","{key}")' in view,f'Editor Layout entry missing: {label} / {key}')
req(view.index('(3,"Toolbar Top / Find Bottom"') < view.index('(1,"Toolbar Top / Find Top"') < view.index('(4,"Toolbar Bottom / Find Top"') < view.index('(2,"Toolbar Bottom / Find Bottom"'),'Editor Layout menu order drifted')
req('self.workspace_layout = 3' in preferences and 'data.get("workspace_layout", 3)' in preferences,'Toolbar Top / Find Bottom is not the unsaved/default layout')
for label,percent,key in (("1.0",100,"Ctrl+1"),("1.15",115,"Ctrl+2"),("1.5",150,"Ctrl+3"),("2.0",200,"Ctrl+4")):
    req(f'("{label}",{percent},"{key}")' in fmt,f'Line Spacing shortcut missing: {key}')
req('for theme,label in (("light","Light"),("dark","Dark"),("system","System")):' in settings,'App Theme action family changed unexpectedly')
for key in ('Ctrl+Alt+Shift+1','Ctrl+Alt+Shift+2','Ctrl+Alt+Shift+3'):
    req(key not in settings,f'App Theme still owns {key}')
req('QKeySequence("Ctrl+Alt+Shift+T")' in view,'Ribbon/Retro toggle shortcut missing')
req('Clear Colour' not in colour and 'clear_colour' not in colour,'Clear Colour was added despite explicit exclusion')
# Prove the layout and formatting/theme engines themselves did not change from 1.0.10.
for name,expected_hash in {
    'apply_workspace_layout':'526a15db728116d0eb83d3e4665d44b6d4157109b423dd0df359fa43993dc58b',
    'set_workspace_layout':'22f5d9b9456e4a97b6fe0d565a160d61a4fdfe0fe21051c3e8c1615e5604b721',
    'set_line_spacing':'fc8deca60c18a66775d73eaab1337655f984d2c796c25e60f4f7512ad30c33be',
    'set_appimage_theme':'6d6fc0249ccfbfb3bb9d8689ac41ef960d28e86a721d8d03fb9cf77b7b1d3a3c',
}.items():
    got,_=fhash(source,'RiqatonyPad',name); req(got==expected_hash,f'out-of-scope engine changed: {name}')
protected={
 'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8',
 'rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb',
 'rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41',
 'widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310',
}
for path,h in protected.items(): req(sha(path)==h,f'protected out-of-scope file changed: {path}')
if errors:
    print('RiqatonyPad 1.0.11 shortcut/layout check failed:')
    [print('- '+e) for e in errors]
    raise SystemExit(1)
print('PASS: RiqatonyPad 1.0.11 bounded shortcut/layout refinement contract')
