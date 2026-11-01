#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.13 bounded UI cleanup gate."""
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
req('APP_VERSION = "1.0.13"' in source,'1.0.13 identity missing')
# Approved wording/tooltip scope only.
spacing='Line Spacing — 1.0 Ctrl+1; 1.15 Ctrl+2; 1.5 Ctrl+3; 2.0 Ctrl+4'
req(source.count(f'setToolTip("{spacing}")')>=2,'Line Spacing tooltips are not aligned with Rico Plus')
req('"Paste as Plain Text"' in source,'Paste as Plain Text label missing')
req('"Paste Plain Text"' not in source,'retired Paste Plain Text label remains')
req('self.tutorial_action.setToolTip("Quick Tour… (Shift+F1)")' in source,'Quick Tour tooltip ellipsis missing')
# Checkbox must live in wizard footer-left, not page content.
for frag in (
    'wizard.setButton(QWizard.WizardButton.CustomButton1,startup_checkbox)',
    'wizard.setOption(QWizard.WizardOption.HaveCustomButton1,True)',
    'QWizard.WizardButton.CustomButton1,QWizard.WizardButton.Stretch,QWizard.WizardButton.BackButton,QWizard.WizardButton.NextButton,QWizard.WizardButton.FinishButton,QWizard.WizardButton.CancelButton',
    'wizard.setOption(QWizard.WizardOption.NoBackButtonOnStartPage,True)',
): req(frag in source,f'Quick Tour footer/navigation contract missing: {frag}')
# Content and page shape are a hard no-edit boundary.
tree=ast.parse(source)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='show_tutorial_wizard')
calls=[n for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='add_page']
req(len(calls)==7,'Quick Tour page count changed')
rows=[]
for i,node in enumerate(calls):
    if i==0: req(len(node.args)==2,'startup checkbox is still embedded in first Quick Tour content page')
    vals=[]
    for arg in node.args[:2]:
        req(isinstance(arg,ast.Constant) and isinstance(arg.value,str),'Quick Tour title/body is no longer literal')
        vals.append(arg.value if isinstance(arg,ast.Constant) else None)
    rows.append(vals)
payload=json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()
req(hashlib.sha256(payload).hexdigest()=='c4aa0a3cf6a6bb0f96cc0daa395d0f67e61e2136de19588fb135e5ca137bb576','Quick Tour page titles/body content changed')
# Precious editor-support modules remain untouched.
protected={
 'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8',
 'rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb',
 'rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41',
 'widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310',
}
for rel,h in protected.items(): req(sha(rel)==h,f'protected out-of-scope file changed: {rel}')
if errors:
    print('RiqatonyPad 1.0.13 UI cleanup check failed:')
    [print('- '+e) for e in errors]
    raise SystemExit(1)
print('PASS: RiqatonyPad 1.0.13 bounded UI wording/Quick Tour footer contract')
