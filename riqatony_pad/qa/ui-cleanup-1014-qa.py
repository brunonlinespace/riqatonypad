#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.14 Quick Tour tooltip correction gate."""
from __future__ import annotations
import ast, hashlib, json
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
ribbon_source=(ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
req('APP_VERSION = "2.0.0-x13.0"' in source,'1.0.14 identity missing')
req('menu, "Quick Tour…", self.show_tutorial_wizard' in source,'Quick Tour menu label drifted')
req('self.tutorial_action.setToolTip("Quick Tour… — Shift+F1")' in source,'Quick Tour action tooltip is not exact')
req('self.tutorial_action.setProperty("riqatonypad_toolbar_tooltip", "Quick Tour…")' in source,'Quick Tour command-surface tooltip override missing')
req('if explicit:\n            clean=str(explicit).replace("&","").strip()' in ribbon_source,'explicit command-surface tooltip does not preserve ellipsis')
# Preserve Quick Tour content exactly.
tree=ast.parse(source)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='show_tutorial_wizard')
calls=[n for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='add_page']
req(len(calls)==7,'Quick Tour page count changed')
rows=[]
for node in calls:
    vals=[]
    for arg in node.args[:2]:
        req(isinstance(arg,ast.Constant) and isinstance(arg.value,str),'Quick Tour title/body is no longer literal')
        vals.append(arg.value if isinstance(arg,ast.Constant) else None)
    rows.append(vals)
payload=json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()
req(hashlib.sha256(payload).hexdigest()=='e3da652c4ca711bbf1cd1915ee21a75ba7599703905c757df3ea8c09d15e6d55','Quick Tour page titles/body content changed')
protected={
 'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8',
 'rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb',
 'rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41',
 'widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310',
}
for rel,h in protected.items(): req(sha(rel)==h,f'protected out-of-scope file changed: {rel}')
if errors:
    print('RiqatonyPad 1.0.14 check failed:')
    [print('- '+e) for e in errors]
    raise SystemExit(1)
print('PASS: RiqatonyPad 1.0.14 Quick Tour tooltip correction contract')
