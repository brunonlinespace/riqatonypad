#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.4 file-lifecycle and status-order gate."""
from __future__ import annotations

import ast
import copy
import os
import shutil
import tempfile
import types
from pathlib import Path

from source_contract import contract_text
root = Path(__file__).resolve().parents[1]
source = contract_text(root)
source += '\n' + (root/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
lifecycle_source=(root/'widgets/rwpyn/editor_lifecycle.py').read_text(encoding='utf-8')
module = ast.parse(source)
riqatonypad = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == "RiqatonyPad")
methods = {n.name: n for n in riqatonypad.body if isinstance(n, ast.FunctionDef)}
command_cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'EditorCommandsAppearanceMixin')
command_methods = {n.name:n for n in command_cls.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(command_methods)
methods.update(command_methods)
lifecycle_cls=next(n for n in ast.parse(lifecycle_source).body if isinstance(n,ast.ClassDef) and n.name=="EditorFileLifecycleMixin")
lifecycle_methods={n.name:n for n in lifecycle_cls.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(lifecycle_methods)
methods.update(lifecycle_methods)

ribbon_source=(root/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
ribbon_cls=next(n for n in ast.parse(ribbon_source).body if isinstance(n,ast.ClassDef) and n.name=='EditorRibbonRetroMixin')
ribbon_methods={n.name:n for n in ribbon_cls.body if isinstance(n,ast.FunctionDef)}
prefs_source=(root/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
prefs_tree=ast.parse(prefs_source)
prefs_cls=next(n for n in prefs_tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorPreferencesMixin')
prefs_methods={n.name:n for n in prefs_cls.body if isinstance(n,ast.FunctionDef)}
def seg(name: str) -> str:
    if name in lifecycle_methods: return ast.get_source_segment(lifecycle_source,lifecycle_methods[name]) or ""
    if name in prefs_methods: return ast.get_source_segment(prefs_source,prefs_methods[name]) or ""
    if name in ribbon_methods: return ast.get_source_segment(ribbon_source,ribbon_methods[name]) or ""
    return ast.get_source_segment(source,methods[name]) or ""

# Status bar must match the Plus component exactly in semantic order.
build = seg("build_ui")
status_order = (
    "self.app_status_bar.addWidget(self.operation_mode_label); "
    "self.app_status_bar.addWidget(self.zoom_label); "
    "self.app_status_bar.addWidget(self.counter_label); "
    "self.app_status_bar.addWidget(self.status_message_label,1)"
)
assert status_order in build
assert "addPermanentWidget(self.zoom_label)" not in build

# Save As must write independently before rebinding the live path.
save_as = seg("save_as_file")
assert "target_path=target_path" in save_as
assert "self._write_payload_atomically(payload, target_path=target_path)" in save_as
write_at = save_as.index("self._write_payload_atomically(payload, target_path=target_path)")
rebind_at = save_as.index("self.file_path = target_path")
assert write_at < rebind_at
assert "forbidden_paths=()" in save_as and "candidate in forbidden" in save_as

writer = seg("_write_payload_atomically")
assert "target_path=None" in writer
assert "destination = os.path.abspath(target_path or self.file_path)" in writer

# Standalone watcher adapts Plus plumbing only; the user-visible conflict surface
# must be the same persistent warning model rather than a RiqatonyPad-only modal.
for required in (
    "QFileSystemWatcher",
    "self._file_watcher.fileChanged.connect(self._schedule_external_change_check)",
    "self._file_watcher.directoryChanged.connect(self._schedule_external_change_check)",
):
    assert required in source, required
for method in (
    "_rebind_file_watcher",
    "_set_backing_state",
    "_set_external_change_pending",
    "_has_external_change",
    "_refresh_backing_state_from_disk",
    "_schedule_external_change_check",
    "_check_external_change_from_watcher",
    "_reload_external_change",
    "_save_version_as",
):
    assert method in methods, method
assert "_show_live_external_change_dialog" not in methods
assert 'QLabel("This file changed on disk after it was opened."' in build
assert 'QPushButton("Reload from Disk"' in build
assert 'QPushButton("Save Version As…"' in build
assert 'self.external_banner.hide()' in build
assert '"Later"' not in source
layout = seg("apply_workspace_layout")
assert '"external_banner"' in layout
assert "self.external_banner.setVisible(bool(self._external_change_pending))" in layout
watcher = seg("_check_external_change_from_watcher")
assert 'self._set_backing_state("missing")' in watcher
assert 'self._set_backing_state("changed")' in watcher
assert 'self._set_backing_state("normal")' in watcher
assert "QMessageBox" not in watcher

save_version = seg("_save_version_as")
assert 'dialog_title="Save Version As — RiqatonyPad"' in save_version
assert "forbidden_paths=(source_path,)" in save_version
assert "external disk copy preserved" in save_version
assert "the original path remains missing" in save_version

external = seg("_external_change_action")
assert '"missing" if current_signature is None else "changed"' in external
assert '"This file is no longer available at its original disk path."' in external
assert '"Save Version As…"' in external
assert 'return "save_version_as"' in external
assert '"Overwrite"' in external  # explicit destructive choice remains available at save time
save = seg("save_file")
assert 'if action=="save_version_as": return self._save_version_as()' in save
assert "self._rebind_file_watcher(self.file_path)" in save

# Ordinary Save As inherits Save Version As protection while a conflict exists,
# including a second signature check if the source changes while the file picker is open.
save_as = seg("save_as_file")
assert "if not forbidden_paths and self._has_external_change():" in save_as
assert "return self._save_version_as()" in save_as
assert "if old_path and target_path == old_path:" in save_as
assert save_as.count("self._has_external_change()") >= 2

# Dirty Duplicate and External Editor choices are explicit and independently remembered.
dup = seg("duplicate_current_file")
assert '"Duplicate Current Document"' in dup
assert '"Duplicate Last Saved Version"' in dup
assert 'QCheckBox("Remember this choice"' in dup
assert 'self.set_dirty_duplicate_action(choice)' in dup
assert 'payload = read_bounded_bytes(source, MAX_FILE_SIZE, label="saved document")' in dup
assert 'payload = self._document_payload("rtf")' in dup
assert 'os.path.lexists(destination)' in dup
assert 'self._install_new_file_no_replace(temporary, destination)' in dup
assert 'os.replace(temporary, destination)' not in dup

# Execute the dependency-free installer method itself. It must install a new
# destination successfully and preserve both pre-existing and raced paths.
installer_node = copy.deepcopy(methods["_install_new_file_no_replace"])
installer_node.decorator_list = []
installer_module = ast.Module(body=[installer_node], type_ignores=[])
ast.fix_missing_locations(installer_module)
installer_globals = {"os": os, "shutil": shutil, "RuntimeError": RuntimeError}
exec(compile(installer_module, str(root / "app.py"), "exec"), installer_globals)
install_no_replace = installer_globals["_install_new_file_no_replace"]

with tempfile.TemporaryDirectory(prefix="riqatonypad-no-clobber-") as folder:
    folder_path = Path(folder)
    temporary = folder_path / ".duplicate.tmp"
    destination = folder_path / "copy.rtf"
    temporary.write_bytes(b"new duplicate")
    install_no_replace(str(temporary), str(destination))
    assert destination.read_bytes() == b"new duplicate"
    assert not temporary.exists()

    temporary = folder_path / ".duplicate-existing.tmp"
    destination = folder_path / "existing.rtf"
    temporary.write_bytes(b"must not replace")
    destination.write_bytes(b"keep me")
    try:
        install_no_replace(str(temporary), str(destination))
    except RuntimeError:
        pass
    else:
        raise AssertionError("existing duplicate destination was overwritten")
    assert destination.read_bytes() == b"keep me"

    if hasattr(os, "symlink"):
        temporary = folder_path / ".duplicate-symlink.tmp"
        destination = folder_path / "existing-link.rtf"
        link_target = folder_path / "link-target.rtf"
        temporary.write_bytes(b"must not replace link")
        link_target.write_bytes(b"keep link target")
        try:
            os.symlink(link_target.name, destination)
        except OSError:
            pass
        else:
            try:
                install_no_replace(str(temporary), str(destination))
            except RuntimeError:
                pass
            else:
                raise AssertionError("existing symlink destination was overwritten")
            assert destination.is_symlink()
            assert link_target.read_bytes() == b"keep link target"

    # Force the portable exclusive-create fallback and verify the same contract.
    real_link = os.link
    try:
        os.link = lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("no hard links"))
        temporary = folder_path / ".duplicate-fallback.tmp"
        destination = folder_path / "fallback-existing.rtf"
        temporary.write_bytes(b"must not replace fallback")
        destination.write_bytes(b"keep fallback")
        try:
            install_no_replace(str(temporary), str(destination))
        except RuntimeError:
            pass
        else:
            raise AssertionError("fallback overwrote an existing destination")
        assert destination.read_bytes() == b"keep fallback"
    finally:
        os.link = real_link

external_editor = seg("open_external_editor")
assert '"Save Changes and Open"' in external_editor
assert '"Open Last Saved Version"' in external_editor
assert 'QCheckBox("Remember this choice"' in external_editor
assert 'self.set_dirty_external_action(choice)' in external_editor
assert "if not self.save_file():" in external_editor

settings = seg("make_settings_menu")
assert 'menu.addMenu("File Handling")' not in settings
assert '"Duplicate File with Unsaved Changes"' in settings
assert '"Open Externally with Unsaved Changes"' in settings
assert '("ask","Duplicate Current Document")' not in settings  # Ask remains its own policy label.
assert '"Ask Every Time"' in settings

# Rename/delete are non-clobbering and verify identity/content around confirmation.
rename = seg("rename_current_file")
assert "os.path.lexists(new_path)" in rename
assert "self._rename_path_no_replace(old_path, new_path)" in rename
assert "self._path_identity(old_path) != expected_identity" in rename
assert "self._disk_signature(old_path) != expected_signature" in rename
delete = seg("delete_current_file")
assert "self._path_identity(path) != expected_identity" in delete
assert "self._disk_signature(path) != expected_signature" in delete
assert "self.check_save_changes()" in delete

# Preference persistence must be explicit and bounded to known values.
load_prefs = seg("load_preferences")
save_prefs = seg("save_preferences")
for key in ("dirty_duplicate_action", "dirty_external_action"):
    assert key in load_prefs and key in save_prefs

assert "Focused Mode" not in source
print("PASS: RiqatonyPad 1.0.4 file lifecycle, missing-backing safety and Plus status-order parity")
