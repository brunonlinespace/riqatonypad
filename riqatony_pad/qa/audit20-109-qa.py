#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.11 Audit 20 Quick Tour naming/content gate."""
from pathlib import Path
import ast, hashlib
from source_contract import contract_text
from shortcut_legacy import legacy_read_bytes
ROOT=Path(__file__).resolve().parents[1]; errors=[]
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
req('APP_VERSION = "2.0.0-x13.0"' in source,'1.0.11 identity missing')
for fragment in (
    '("Help", "tutorial", "Quick Tour", "action", "tutorial_action", "tutorial")',
    'menu, "Quick Tour…", self.show_tutorial_wizard,',
    'self.tutorial_action.setToolTip("Quick Tour… — Shift+F1")',
    'wizard.setWindowTitle("Quick Tour — RiqatonyPad")',
): req(fragment in source,f'Quick Tour alignment missing: {fragment}')
# User-facing old name must be gone; the internal method name is intentionally retained.
req('"Tutorial Wizard"' not in source,'stale user-facing Tutorial Wizard literal remains')
req('def show_tutorial_wizard(self):' in source,'internal tour implementation was renamed unnecessarily')
# Freshness audit: protect the already-current content without rewriting it.
for fragment in (
    '<b>Ctrl+F</b> opens the Find/Replace panel', '<b>Ctrl+H</b> focuses Replace',
    '<b>F3</b> for the next result', '<b>Shift+F3</b>', 'Editor Layout',
    'Locked Mode protects a document', 'Ctrl+mouse-wheel zooms the document',
    'Choose <b>Ribbon</b> or <b>Retro</b>', 'Customise Retro Bar…',
    'New Document Defaults controls the exact font', 'Use <b>F1</b> for the bundled RTF Documentation',
): req(fragment in source,f'current Quick Tour content missing: {fragment}')
# Protect unrelated core modules exactly.
protected={
 'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8',
 'rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb',
 'rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41',
 'widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310',
}
for r,h in protected.items(): req(sha(r)==h,f'protected out-of-scope file changed: {r}')
if errors:
    print('RiqatonyPad 1.0.11 Audit 20 check failed:'); [print(f'- {e}') for e in errors]; raise SystemExit(1)
print('PASS: RiqatonyPad 1.0.11 Audit 20 Quick Tour naming/content contract')
