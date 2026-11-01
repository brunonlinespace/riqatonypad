#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.11 Audit 24 clean-load undo/redo regression gate."""
from __future__ import annotations
import hashlib
from pathlib import Path
from shortcut_legacy import legacy_read_bytes
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def req(c,m):
    if not c: errors.append(m)
def src(r): return (ROOT/r).read_text(encoding="utf-8")
def sha(rel):
    data=legacy_read_bytes(ROOT, rel)
    if rel in ("rtf_new_document.py", "widgets/shortcut_search.py"):
        assert data.startswith(b"#!/usr/bin/env python3\n"), f"x12.2 approved shebang missing: {rel}"
        data=data[len(b"#!/usr/bin/env python3\n"):]
    return hashlib.sha256(data).hexdigest()
editor=src("app.py")
lifecycle=src("widgets/rwpyn/editor_lifecycle.py")
req('APP_VERSION = "2.0.0-x13.0"' in editor,"1.0.11 identity missing")
start=lifecycle.index('    def load_file(')
end=lifecycle.index('    @staticmethod\n    def _default_created_file_mode',start)
load=lifecycle[start:end]
req('populate_qtextdocument_from_rtf_model(' in load,"direct RTF import path missing")
req('self.visual_editor.setHtml(document_html)' in load,"RTF fallback import path missing")
req('self.visual_editor.document().clearUndoRedoStacks()' in load,"successful RTF load must clear load-generated undo/redo history")
req('self.visual_editor.document().setModified(False)' in load,"successful RTF load must mark document clean")
req(load.index('clearUndoRedoStacks()') < load.index('setModified(False)'),"undo/redo history must be cleared before the document is marked clean")
# 1.0.9 deliberately leaves the shared RTF/support/search/new-document modules unchanged from 1.0.5.
protected={
 'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8',
 'rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb',
 'rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41',
 'widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310',
}
for r,h in protected.items(): req(sha(r)==h,f"protected out-of-scope 1.0.5 file changed: {r}")
if errors:
    print("RiqatonyPad 1.0.11 Audit 24 check failed:")
    [print(f"- {e}") for e in errors]
    raise SystemExit(1)
print("PASS: RiqatonyPad 1.0.11 Audit 24 clean-load undo/redo history contract")
