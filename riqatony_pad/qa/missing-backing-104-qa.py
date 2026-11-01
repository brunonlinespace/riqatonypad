#!/usr/bin/env python3
"""RiqatonyPad 1.0.4 Audit 3 missing-backing survival gate."""
from pathlib import Path
import ast
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
source=contract_text(ROOT)
module=ast.parse(source)
cls=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
methods={n.name:n for n in cls.body if isinstance(n,ast.FunctionDef)}
lifecycle_source=(ROOT/"widgets/rwpyn/editor_lifecycle.py").read_text(encoding="utf-8")
lifecycle_cls=next(n for n in ast.parse(lifecycle_source).body if isinstance(n,ast.ClassDef) and n.name=="EditorFileLifecycleMixin")
lifecycle_methods={n.name:n for n in lifecycle_cls.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(lifecycle_methods)
methods.update(lifecycle_methods)
def seg(name): return ast.get_source_segment(lifecycle_source if name in lifecycle_methods else source,methods[name]) or ''

assert 'self._backing_state = "normal"' in source
for name in ('_set_backing_state','_refresh_backing_state_from_disk','_confirm_missing_backing_preservation'):
    assert name in methods,name
state=seg('_set_backing_state')
for token in ('{"normal", "changed", "missing"}','self._external_change_pending = state != "normal"','reload_button.setEnabled(False)','Reload is unavailable'):
    assert token in state,token
watch=seg('_check_external_change_from_watcher')
assert 'current_signature is None' in watch and 'self._set_backing_state("missing")' in watch
assert 'self._set_backing_state("changed")' in watch and 'self._set_backing_state("normal")' in watch
assert 'QMessageBox' not in watch
refresh=seg('_refresh_backing_state_from_disk')
for token in ('current_signature is None','current_signature == self.file_disk_signature','self._set_backing_state("missing")','self._set_backing_state("changed")','self._set_backing_state("normal")'):
    assert token in refresh,token
close_guard=seg('_confirm_missing_backing_preservation')
for label in ('"Backing File Missing"','"Save Version As…"','"Recreate Original…"','"Close Without Saving"'):
    assert label in close_guard,label
assert 'return self._save_version_as()' in close_guard
assert 'return self.save_file()' in close_guard
check=seg('check_save_changes')
assert check.index('self._refresh_backing_state_from_disk()') < check.index('if self.content_saved:')
assert 'if self._backing_state == "missing":' in check and 'return self._confirm_missing_backing_preservation()' in check
save_exit=seg('save_and_exit')
assert 'self._refresh_backing_state_from_disk()' in save_exit
assert 'self._confirm_missing_backing_preservation()' in save_exit
external=seg('_external_change_action')
for token in ('"missing" if current_signature is None else "changed"','"This file is no longer available at its original disk path."','Overwrite explicitly recreates the original path.','reload_button.setEnabled(current_signature is not None)'):
    assert token in external,token
save_version=seg('_save_version_as')
assert 'source_was_missing = self._backing_state == "missing"' in save_version
assert '"the original path remains missing."' in save_version
# Guardrail: standalone adaptation only, no Plus multi-document infrastructure.
for forbidden in ('OpenDocumentMonitor','EditorManager','DocumentRepository','workspace_scanner'):
    assert forbidden not in source,forbidden
# Existing lightweight watcher remains file + parent directory based.
rebind=seg('_rebind_file_watcher')
assert 'watcher.addPath(parent)' in rebind and 'watcher.addPath(target)' in rebind
print('PASS: RiqatonyPad 1.0.4 Audit 3 missing-backing survival contract')
