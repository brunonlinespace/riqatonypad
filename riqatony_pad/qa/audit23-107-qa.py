#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.11 Audit 23 Delete-preservation regression gate."""
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
start=lifecycle.index('    def delete_current_file(')
end=lifecycle.index('    def _document_is_dirty(',start)
delete=lifecycle[start:end]
# Existing destructive-operation protections remain mandatory.
for fragment in (
    'source_path = os.path.abspath(self.file_path)',
    'self.check_save_changes()',
    'os.path.abspath(self.file_path) != source_path',
    'self.load_file(',
    'check_changes=False, show_error=False',
    'expected_identity = self._path_identity(path)',
    'expected_signature = self._disk_signature(path)',
    'expected_signature != self.file_disk_signature',
    'self._path_identity(path) != expected_identity',
    'self._disk_signature(path) != expected_signature',
    'os.remove(path)',
    'fsync_directory(os.path.dirname(path) or os.curdir)',
): req(fragment in delete,f"Audit 23 delete contract missing: {fragment}")
# Match Plus open-document preservation semantics.
for fragment in (
    'The open document will be retained so it can be saved elsewhere or recreated.',
    'self._check_external_change_from_watcher()',
    'Removed {os.path.basename(path)} from disk; open document retained',
): req(fragment in delete,f"Audit 23 preservation contract missing: {fragment}")
req('self.new_file()' not in delete,"Delete must not replace the retained live document with a new blank document")
remove_i=delete.index('os.remove(path)')
resolve_i=delete.index('self._check_external_change_from_watcher()')
req(remove_i < resolve_i,"backing-path state must be resolved only after successful disk removal")
# The retained live document relies on the already-reviewed Audit 3 lifecycle.
for fragment in (
    'def _confirm_missing_backing_preservation(self):',
    '"Save Version As…"',
    '"Recreate Original…"',
    '"Close Without Saving"',
    'if self._backing_state == "missing":',
): req(fragment in editor+lifecycle,f"existing Audit 3 missing-backing contract changed: {fragment}")
# Shared editor/RTF helpers remain byte-for-byte at the 1.0.6 baseline.
protected={
 'rtf_codec.py':'598938f533f0b562c55c901d46daef1c6de8bc788ff96eeed387d428737666b8',
 'rich_text_support.py':'6c6d7152ad306788a72d420401a4563506e72150c389e80a61a5bdbc8d235fdb',
 'rtf_new_document.py':'539058c822ebb5e5360b6b03f610b3ef9fc8d8196a662e402815622a05f32a41',
 'widgets/shortcut_search.py':'c9ea5e80ffca4f5523873c5b9035e17cf802f83f0b78fa611ff0ca66d1b63310',
}
for r,h in protected.items(): req(sha(r)==h,f"protected out-of-scope 1.0.6 file changed: {r}")
if errors:
    print("RiqatonyPad 1.0.11 Audit 23 check failed:")
    [print(f"- {e}") for e in errors]
    raise SystemExit(1)
print("PASS: RiqatonyPad 1.0.11 Audit 23 open-document Delete preservation contract")
