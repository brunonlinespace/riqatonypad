#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.12 Quick Tour/icon refinement gate."""
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
source=contract_text(ROOT)+'\n'+(ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
ribbon_source=(ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
req('APP_VERSION = "2.0.0-x13.0"' in source,'1.0.12 identity missing')
req('RIBBON_BUTTON_SIZE = 52' in ribbon_source,'52x52 command-button size changed')
req('RIBBON_ICON_SIZE = 36' in ribbon_source,'36x36 command-icon size missing')
req('menu, "Quick Tour…", self.show_tutorial_wizard,' in source,'Help menu Quick Tour ellipsis missing')
req('self.tutorial_action.setToolTip("Quick Tour… — Shift+F1")' in source,'Quick Tour tooltip/shortcut changed unexpectedly')
req('wizard.setOption(QWizard.WizardOption.NoBackButtonOnStartPage,True)' in source,'first-page Back suppression missing')
req('QCheckBox("Don\'t show Quick Tour on startup again",wizard)' in source,'Quick Tour startup checkbox missing')
req('startup_checkbox.setChecked(bool(self.tutorial_seen))' in source,'Quick Tour checkbox does not reflect persisted state')
req('self.tutorial_seen=bool(checked); self.save_preferences()' in source,'Quick Tour checkbox does not persist through existing preference path')
req('startup_checkbox.toggled.connect(set_tour_startup_disabled)' in source,'Quick Tour checkbox persistence wiring missing')
# Showing the tour must not itself suppress future startup display.
req('self.tutorial_seen = True' not in source,'Quick Tour is still auto-marked suppressed merely by being shown')
req('if not self.tutorial_seen and not (SMOKE_TEST_MODE or FORMAT_PARITY_PROBE_MODE):\n            QTimer.singleShot(0, self.show_tutorial_wizard)' in source,'startup Quick Tour trigger drifted')
# The existing page titles/body strings are a hard no-edit boundary.
tree=ast.parse(source)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='show_tutorial_wizard')
rows=[]
for node in ast.walk(fn):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='add_page':
        vals=[]
        for arg in node.args[:2]:
            req(isinstance(arg,ast.Constant) and isinstance(arg.value,str),'Quick Tour title/body is no longer a literal string')
            vals.append(arg.value if isinstance(arg,ast.Constant) else None)
        rows.append(vals)
payload=json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode('utf-8')
req(len(rows)==7,'Quick Tour page count changed')
req(hashlib.sha256(payload).hexdigest()=='e3da652c4ca711bbf1cd1915ee21a75ba7599703905c757df3ea8c09d15e6d55','Quick Tour page titles/body content changed')
# Protect precious/out-of-scope editor-format files exactly.
protected={
 'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8',
 'rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb',
 'rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41',
 'widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310',
}
for rel,h in protected.items(): req(sha(rel)==h,f'protected out-of-scope file changed: {rel}')
if errors:
    print('RiqatonyPad 1.0.12 Quick Tour/icon check failed:')
    [print('- '+e) for e in errors]
    raise SystemExit(1)
print('PASS: RiqatonyPad 1.0.12 bounded Quick Tour/icon refinement contract')
