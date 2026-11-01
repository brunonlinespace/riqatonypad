#!/usr/bin/env python3
# RiqatonyPad - original editor file lifecycle operations
# GPLv3-or-later
# Version: 2.0.0-x10.0

import os
import hashlib
import tempfile
import shutil
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QCheckBox, QInputDialog, QLineEdit
from widgets.rwpyn.editor_printing import APP_NAME, fsync_directory
from widgets.rwpyn.editor_insertion import read_bounded_bytes
from rich_text_support import sanitise_qt_html
from rtf_codec import decode_rtf, document_to_rtf_with_properties, populate_qtextdocument_from_rtf_model, _rtf_clear_automatic_foreground

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MiB responsiveness limit
RTF_EXTENSIONS = {".rtf"}
DOCUMENT_EXTENSIONS = RTF_EXTENSIONS


class EditorFileLifecycleMixin:
    def open_external_editor(self):
        if not self.file_path:
            QMessageBox.information(self, "External Editor — RiqatonyPad", "Save the file first.")
            return False

        dirty = self._document_is_dirty()
        choice = self.dirty_external_action if dirty else "saved"
        if dirty and choice == "ask":
            dialog = QMessageBox(self)
            dialog.setIcon(QMessageBox.Icon.Question)
            dialog.setWindowTitle("Unsaved Changes — External Editor")
            dialog.setText("This document has unsaved changes.")
            dialog.setInformativeText(
                "Choose whether to save the current RiqatonyPad document before opening it "
                "externally, or open the last version already stored on disk."
            )
            save_button = dialog.addButton("Save Changes and Open", QMessageBox.ButtonRole.AcceptRole)
            saved_button = dialog.addButton("Open Last Saved Version", QMessageBox.ButtonRole.ActionRole)
            cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
            remember = QCheckBox("Remember this choice", dialog)
            dialog.setCheckBox(remember)
            dialog.setDefaultButton(save_button)
            dialog.setEscapeButton(cancel_button)
            dialog.exec()
            clicked = dialog.clickedButton()
            if clicked is save_button:
                choice = "save"
            elif clicked is saved_button:
                choice = "saved"
            else:
                return False
            if remember.isChecked():
                self.set_dirty_external_action(choice)

        if choice == "save":
            if not self.save_file():
                return False
        elif choice != "saved":
            return False

        if not self.file_path or not os.path.isfile(self.file_path):
            QMessageBox.warning(self, "External Editor — RiqatonyPad", "The saved disk version is no longer available.")
            return False
        opened = self._open_host_target(self.file_path, local=True)
        if not opened:
            QMessageBox.warning(self, "External Editor — RiqatonyPad", "The desktop could not open this file.")
        else:
            self._show_status_message(f"Opened {os.path.basename(self.file_path)} in an external editor.", 3000)
        return bool(opened)


    def open_containing_folder(self):
        if not self.file_path:
            QMessageBox.information(self, "Open Containing Folder — RiqatonyPad", "Save the file first.")
            return False
        folder = os.path.dirname(os.path.abspath(self.file_path))
        opened = self._open_host_target(folder, local=True)
        if not opened:
            QMessageBox.warning(self, "Open Containing Folder — RiqatonyPad", "The desktop could not open this folder.")
        else:
            self._show_status_message(f"Opened the folder containing {os.path.basename(self.file_path)}.", 3000)
        return bool(opened)


    def duplicate_current_file(self):
        if not self.file_path:
            QMessageBox.information(self, "Duplicate File — RiqatonyPad", "Save the file first.")
            return False

        source = os.path.abspath(self.file_path)
        dirty = self._document_is_dirty()
        choice = self.dirty_duplicate_action if dirty else "current"
        if dirty and choice == "ask":
            dialog = QMessageBox(self)
            dialog.setIcon(QMessageBox.Icon.Question)
            dialog.setWindowTitle("Unsaved Changes — Duplicate File")
            dialog.setText("This document has unsaved changes.")
            dialog.setInformativeText(
                "Choose whether the duplicate should contain the current RiqatonyPad document "
                "including unsaved edits, or the last version stored on disk."
            )
            current_button = dialog.addButton("Duplicate Current Document", QMessageBox.ButtonRole.AcceptRole)
            saved_button = dialog.addButton("Duplicate Last Saved Version", QMessageBox.ButtonRole.ActionRole)
            cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
            remember = QCheckBox("Remember this choice", dialog)
            dialog.setCheckBox(remember)
            dialog.setDefaultButton(current_button)
            dialog.setEscapeButton(cancel_button)
            dialog.exec()
            clicked = dialog.clickedButton()
            if clicked is current_button:
                choice = "current"
            elif clicked is saved_button:
                choice = "saved"
            else:
                return False
            if remember.isChecked():
                self.set_dirty_duplicate_action(choice)

        stem, suffix = os.path.splitext(source)
        candidate = stem + " copy" + suffix
        counter = 2
        while os.path.exists(candidate):
            candidate = f"{stem} copy {counter}{suffix}"
            counter += 1
        destination, _ = QFileDialog.getSaveFileName(
            self, "Duplicate File — RiqatonyPad", candidate, "Rich Text Format (*.rtf)"
        )
        if not destination:
            return False
        if not Path(destination).suffix:
            destination += ".rtf"
        if Path(destination).suffix.lower() not in RTF_EXTENSIONS:
            QMessageBox.warning(self, "Duplicate File — RiqatonyPad", "RiqatonyPad duplicates .rtf documents only.")
            return False
        destination = os.path.abspath(destination)
        if destination == source:
            QMessageBox.warning(self, "Duplicate File — RiqatonyPad", "Choose a different filename for the duplicate.")
            return False
        if os.path.lexists(destination):
            QMessageBox.warning(
                self, "Duplicate File — RiqatonyPad",
                f"'{os.path.basename(destination)}' already exists. Choose a new filename."
            )
            return False

        try:
            if choice == "saved":
                payload = read_bounded_bytes(source, MAX_FILE_SIZE, label="saved document")
            elif choice == "current":
                if (
                    not dirty
                    and self._source_rtf_payload is not None
                    and self._disk_signature(source) == self.file_disk_signature
                ):
                    payload = bytes(self._source_rtf_payload)
                else:
                    payload = self._document_payload("rtf")
            else:
                return False
            if len(payload) > MAX_FILE_SIZE:
                raise ValueError(
                    f"The duplicate would exceed RiqatonyPad's {MAX_FILE_SIZE//(1024*1024)} MiB reopen limit."
                )
            parent = os.path.dirname(destination) or os.curdir
            os.makedirs(parent, exist_ok=True)
            descriptor, temporary = tempfile.mkstemp(prefix=".riqatonypad-duplicate-", dir=parent)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                if os.path.exists(source):
                    os.chmod(temporary, os.stat(source).st_mode & 0o777)
                self._install_new_file_no_replace(temporary, destination)
                temporary = None
                fsync_directory(parent)
            finally:
                if temporary:
                    try:
                        os.remove(temporary)
                    except OSError:
                        pass
        except (OSError, ValueError, RuntimeError, MemoryError) as exc:
            QMessageBox.critical(self, "Duplicate File — RiqatonyPad", f"Could not duplicate the file:\n{exc}")
            return False
        self._show_status_message(f"Duplicated as {os.path.basename(destination)}.", 4000)
        return True


    def delete_current_file(self):
        if not self.file_path:
            QMessageBox.information(self, "Delete File — RiqatonyPad", "Save the file first.")
            return False
        source_path = os.path.abspath(self.file_path)
        if self._document_is_dirty():
            if not self.check_save_changes():
                return False
            # Match Rico Plus: Save Version As can rebind the live document.
            # Never let the pending delete continue against that newly adopted path.
            if not self.file_path or os.path.abspath(self.file_path) != source_path:
                return False
            # Match Rico Plus: if the user chose Discard, reload the saved disk
            # version before deletion so discarded edits cannot survive in the
            # live document that will be retained after its backing file is removed.
            if self._document_is_dirty() and not self.load_file(
                self.file_path, check_changes=False, show_error=False
            ):
                return False

        path = source_path
        expected_identity = self._path_identity(path)
        expected_signature = self._disk_signature(path)
        if expected_identity is None or expected_signature is None:
            QMessageBox.warning(self, "Delete File — RiqatonyPad", "The file is no longer available. Nothing was deleted.")
            return False
        if self.file_disk_signature is not None and expected_signature != self.file_disk_signature:
            self._set_external_change_pending(True)
            QMessageBox.warning(
                self,
                "Delete Cancelled — RiqatonyPad",
                "The file changed outside RiqatonyPad. Review the external version before deleting anything.",
            )
            return False

        answer = QMessageBox.warning(
            self,
            "Delete File? — RiqatonyPad",
            f"Permanently delete {os.path.basename(path)}?\n\nThis action cannot be undone."
            "\n\nThe open document will be retained so it can be saved elsewhere or recreated.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False
        if self._path_identity(path) != expected_identity or self._disk_signature(path) != expected_signature:
            QMessageBox.warning(
                self,
                "Delete Cancelled — RiqatonyPad",
                "The file changed or was replaced after the confirmation dialog. Nothing was deleted.",
            )
            return False
        try:
            os.remove(path)
            fsync_directory(os.path.dirname(path) or os.curdir)
        except OSError as exc:
            QMessageBox.critical(self, "Delete File — RiqatonyPad", f"Could not delete the file:\n{exc}")
            return False

        # Reuse the existing Audit 3 backing-path resolver exactly as Rico Plus
        # calls its live EditorPage backing-path handler after removing the file.
        # Expected deletion: refresh the existing backing-state banner without
        # also announcing an unrelated external-file disappearance.
        self._expected_delete_message = True
        try:
            self._check_external_change_from_watcher()
        finally:
            self._expected_delete_message = False
        self._show_status_message(
            f"Deleted {os.path.basename(path)}; open document retained.", 4000
        )
        return True


    def _document_is_dirty(self):
        return (not self.content_saved) or self.visual_editor.document().isModified()


    @staticmethod
    def _path_identity(file_path):
        try:
            details = os.lstat(file_path)
        except OSError:
            return None
        return (details.st_dev, details.st_ino, details.st_mode & 0o170000)


    @staticmethod
    def _install_new_file_no_replace(temporary, destination):
        """Install a synchronized temporary file without overwriting a raced path."""
        try:
            os.link(temporary, destination, follow_symlinks=False)
        except FileExistsError as exc:
            raise RuntimeError("A file appeared at the duplicate destination. Duplicate was cancelled.") from exc
        except (AttributeError, NotImplementedError, TypeError, OSError):
            descriptor = None
            created = False
            try:
                temporary_mode = os.stat(temporary).st_mode & 0o7777
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                flags |= getattr(os, "O_CLOEXEC", 0)
                descriptor = os.open(destination, flags, temporary_mode)
                created = True
                if hasattr(os, "fchmod"):
                    os.fchmod(descriptor, temporary_mode)
                with open(temporary, "rb") as source_handle, os.fdopen(descriptor, "wb") as target_handle:
                    descriptor = None
                    shutil.copyfileobj(source_handle, target_handle, length=1024 * 1024)
                    target_handle.flush()
                    os.fsync(target_handle.fileno())
            except FileExistsError as exc:
                raise RuntimeError("A file appeared at the duplicate destination. Duplicate was cancelled.") from exc
            except OSError:
                if created:
                    try:
                        os.unlink(destination)
                    except OSError:
                        pass
                raise
            finally:
                if descriptor is not None:
                    try:
                        os.close(descriptor)
                    except OSError:
                        pass
        try:
            os.unlink(temporary)
        except OSError:
            # The destination is already complete. A leftover hidden temporary
            # file is preferable to reporting a false duplicate failure.
            pass


    @staticmethod
    def _rename_path_no_replace(source, destination):
        try:
            os.link(source, destination, follow_symlinks=False)
        except FileExistsError as exc:
            raise RuntimeError("A file appeared at the rename destination. Rename was cancelled.") from exc
        except (AttributeError, NotImplementedError, TypeError, OSError):
            if os.path.lexists(destination):
                raise RuntimeError("A file appeared at the rename destination. Rename was cancelled.")
            os.rename(source, destination)
            return
        try:
            os.unlink(source)
        except OSError:
            try:
                os.unlink(destination)
            except OSError:
                pass
            raise


    def _rebind_file_watcher(self, file_path=None):
        watcher = getattr(self, "_file_watcher", None)
        if watcher is None:
            return
        try:
            existing = watcher.files() + watcher.directories()
            if existing:
                watcher.removePaths(existing)
            target = os.path.abspath(file_path or self.file_path) if (file_path or self.file_path) else None
            if not target:
                return
            parent = os.path.dirname(target) or os.curdir
            if os.path.isdir(parent):
                watcher.addPath(parent)
            if os.path.isfile(target):
                watcher.addPath(target)
        except RuntimeError:
            return


    def _set_backing_state(self, state):
        """Track whether the loaded document's original disk path is normal, changed, or missing."""
        if state not in {"normal", "changed", "missing"}:
            raise ValueError(f"Unknown backing state: {state}")
        self._backing_state = state
        self._external_change_pending = state != "normal"
        if (state == "normal" and getattr(self, "_critical_editor_message", False)
                and getattr(self, "_critical_editor_message_kind", None) == "backing"):
            self._status_message_timer.stop()
            self._clear_status_message()
        banner = getattr(self, "external_banner", None)
        if banner is None:
            return
        reload_button = getattr(self, "external_reload_button", None)
        label = getattr(self, "external_label", None)
        if state == "normal":
            if reload_button is not None:
                reload_button.setEnabled(True)
            if label is not None:
                label.setText("This file changed on disk after it was opened.")
            banner.hide()
            return
        if state == "missing":
            if label is not None:
                label.setText(
                    "This file is no longer available at its original disk path. "
                    "Save Version As preserves the live document; Reload is unavailable."
                )
            if reload_button is not None:
                reload_button.setEnabled(False)
        else:
            if label is not None:
                label.setText("This file changed on disk after it was opened.")
            if reload_button is not None:
                reload_button.setEnabled(True)
        banner.show()


    def _set_external_change_pending(self, pending):
        """Compatibility wrapper for existing conflict callers, preserving a missing state."""
        if not pending:
            self._set_backing_state("normal")
            return
        current_signature = None
        if self.file_path and self.file_disk_signature is not None:
            current_signature = self._disk_signature(self.file_path)
        self._set_backing_state(
            "missing"
            if self.file_path and self.file_disk_signature is not None and current_signature is None
            else "changed"
        )


    def _has_external_change(self):
        if not self.file_path or self.file_disk_signature is None:
            return False
        return self._disk_signature(self.file_path) != self.file_disk_signature


    def _refresh_backing_state_from_disk(self):
        """Reconfirm live backing state synchronously before any discard/close decision."""
        if not self.file_path or self.file_disk_signature is None:
            self._set_backing_state("normal")
            return self._backing_state
        current_signature = self._disk_signature(self.file_path)
        if current_signature is None:
            self._set_backing_state("missing")
        elif current_signature == self.file_disk_signature:
            self._set_backing_state("normal")
        else:
            self._set_backing_state("changed")
        return self._backing_state


    def _schedule_external_change_check(self, _path=None):
        timer = getattr(self, "_external_change_timer", None)
        if timer is not None:
            timer.start()


    def _check_external_change_from_watcher(self):
        if not self.file_path or self.file_disk_signature is None:
            self._set_backing_state("normal")
            self._rebind_file_watcher(self.file_path)
            return
        current_signature = self._disk_signature(self.file_path)
        self._rebind_file_watcher(self.file_path)
        previous_state = self._backing_state
        if current_signature is None:
            self._set_backing_state("missing")
            if previous_state != "missing" and not getattr(self, "_expected_delete_message", False):
                self._show_status_message(
                    "Backing file missing; the live RiqatonyPad document remains protected.",
                    6000, warning_kind="backing"
                )
            return
        if current_signature == self.file_disk_signature:
            self._set_backing_state("normal")
            return
        self._set_backing_state("changed")
        if previous_state != "changed":
            self._show_status_message("File changed outside RiqatonyPad.", 5000, warning_kind="backing")


    def _reload_external_change(self):
        if not self.file_path or not os.path.isfile(self.file_path):
            self._set_backing_state("missing")
            QMessageBox.warning(
                self,
                "Reload — RiqatonyPad",
                "Reload is unavailable because the original disk file is missing. "
                "Use Save Version As to preserve the live document or explicitly recreate the original path.",
            )
            return False
        if self._document_is_dirty():
            response = QMessageBox.question(
                self,
                "Discard Editor Changes",
                "Reloading will discard your unsaved RiqatonyPad changes. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if response != QMessageBox.StandardButton.Yes:
                return False
        return bool(self.load_file(self.file_path, check_changes=False, show_error=True))


    def _save_version_as(self):
        if not self.file_path:
            return self.save_as_file()
        source_was_missing = self._backing_state == "missing"
        source_path = Path(self.file_path).expanduser().resolve(strict=False)
        suffix = source_path.suffix or ".rtf"
        suggested = source_path.with_name(f"{source_path.stem} - RiqatonyPad Version{suffix}")
        counter = 2
        while suggested.exists():
            suggested = source_path.with_name(f"{source_path.stem} - RiqatonyPad Version {counter}{suffix}")
            counter += 1
        saved = self.save_as_file(
            initial_path=str(suggested),
            forbidden_paths=(source_path,),
            dialog_title="Save Version As — RiqatonyPad",
            forbidden_message=(
                "Choose a different filename. The original file changed externally and will be left untouched."
            ),
        )
        if saved:
            if source_was_missing:
                message = (
                    f"Saved RiqatonyPad version as {os.path.basename(self.file_path)}; "
                    "the original path remains missing."
                )
            else:
                message = (
                    f"Saved RiqatonyPad version as {os.path.basename(self.file_path)}; "
                    "external disk copy preserved."
                )
            self._show_status_message(message, 5000)
        return bool(saved)


    @staticmethod
    def _content_signature(data):
        """Return a stable signature for the exact encoded file bytes."""
        return (
            len(data),
            hashlib.sha256(data).digest(),
        )


    @classmethod
    def _disk_signature(cls, file_path):
        """Hash a file so same-size or timestamp-preserved edits are found."""
        if not file_path:
            return None

        digest = hashlib.sha256()
        size = 0
        try:
            stat = os.stat(file_path)
            if stat.st_size > MAX_FILE_SIZE:
                return ("oversize", stat.st_size)
            with open(file_path, "rb") as handle:
                while True:
                    chunk = handle.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MAX_FILE_SIZE:
                        return ("oversize", size)
                    digest.update(chunk)
        except OSError:
            return None

        return (
            size,
            digest.digest(),
        )


    def _external_change_action(self):
        """Ask what to do when the open file changed after it was loaded."""
        if not self.file_path or self.file_disk_signature is None:
            return "overwrite"

        current_signature = self._disk_signature(self.file_path)
        if current_signature == self.file_disk_signature:
            self._set_external_change_pending(False)
            return "overwrite"

        self._set_backing_state("missing" if current_signature is None else "changed")
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("File Changed on Disk")
        if current_signature is None:
            dialog.setText("This file is no longer available at its original disk path.")
            dialog.setInformativeText(
                "Save Version As preserves the current RiqatonyPad document at a new path. "
                "Overwrite explicitly recreates the original path. Reload is unavailable "
                "until a disk copy exists again."
            )
        else:
            dialog.setText("This file has changed on disk since RiqatonyPad opened or saved it.")
            dialog.setInformativeText(
                "Choose Reload to discard the current RiqatonyPad edits and use the disk copy, "
                "Save Version As to preserve both versions, or Overwrite to explicitly replace "
                "the changed disk copy with the current RiqatonyPad document."
            )
        reload_button = dialog.addButton("Reload", QMessageBox.ButtonRole.ActionRole)
        reload_button.setEnabled(current_signature is not None)
        save_version_button = dialog.addButton("Save Version As…", QMessageBox.ButtonRole.ActionRole)
        overwrite_button = dialog.addButton("Overwrite", QMessageBox.ButtonRole.DestructiveRole)
        cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(cancel_button)
        dialog.setEscapeButton(cancel_button)
        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked is reload_button:
            return "reload"
        if clicked is save_version_button:
            return "save_version_as"
        if clicked is overwrite_button:
            return "overwrite"
        return "cancel"


    def _confirm_missing_backing_preservation(self):
        """Protect a clean or dirty live document whose original pathname vanished."""
        if self._backing_state != "missing":
            return True
        filename = os.path.basename(self.file_path) if self.file_path else "This document"
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("Backing File Missing")
        dialog.setText(f"{filename} is no longer available at its original path.")
        dialog.setInformativeText(
            "This open editor may be the only remaining copy. Save Version As preserves it "
            "at a new path. Recreate Original enters the protected Save flow, where Overwrite "
            "is still an explicit confirmation."
        )
        save_version = dialog.addButton("Save Version As…", QMessageBox.ButtonRole.AcceptRole)
        recreate = dialog.addButton("Recreate Original…", QMessageBox.ButtonRole.ActionRole)
        close_without = dialog.addButton(
            "Close Without Saving", QMessageBox.ButtonRole.DestructiveRole
        )
        cancel = dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(save_version)
        dialog.setEscapeButton(cancel)
        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked is save_version:
            return self._save_version_as()
        if clicked is recreate:
            return self.save_file()
        if clicked is close_without:
            return True
        return False


    def check_save_changes(self):
        self._refresh_backing_state_from_disk()
        if self._backing_state == "missing":
            return self._confirm_missing_backing_preservation()
        if self.content_saved:
            return True
        answer = QMessageBox.question(
            self,
            APP_NAME,
            "Do you want to save changes?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Save:
            return self.save_file()
        if answer == QMessageBox.StandardButton.Discard:
            return True
        return False


    @staticmethod
    def format_for_path(file_path):
        return "rtf" if Path(file_path).suffix.lower() in RTF_EXTENSIONS else None


    def _document_payload(self, target_format=None):
        if (target_format or self.file_format) != "rtf": raise ValueError("RiqatonyPad 1.1.2 saves RTF documents only.")
        return document_to_rtf_with_properties(self._unzoomed_visual_document(), self.rtf_document_properties)


    def _synchronise_after_save(self, payload, *, semantic_signature=None, preserve_warnings=False):
        self._loading=True
        try: self.visual_editor.document().setModified(False)
        finally: self._loading=False
        self._source_rtf_payload=bytes(payload)
        if semantic_signature is None:
            try:
                semantic_signature=self._content_signature(self._document_payload("rtf"))
            except Exception:
                semantic_signature=None
        self._source_rtf_semantic_signature=semantic_signature
        if not preserve_warnings:
            self.rtf_compatibility_warnings=()
        self._rtf_save_warning_acknowledged=False


    def _write_payload_atomically(self, payload, *, target_path=None):
        destination = os.path.abspath(target_path or self.file_path)
        if os.path.islink(destination):
            with open(destination, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            return

        parent = os.path.dirname(destination) or "."
        basename = os.path.basename(destination)
        try:
            existing_mode = os.stat(destination).st_mode & 0o7777
        except FileNotFoundError:
            existing_mode = self._default_created_file_mode()

        descriptor = None
        temporary = None
        try:
            descriptor, temporary = tempfile.mkstemp(
                prefix=f".{basename}.riqatonypad-", suffix=".tmp", dir=parent
            )
            if hasattr(os, "fchmod"):
                os.fchmod(descriptor, existing_mode)
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = None
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, destination)
            temporary = None
            fsync_directory(parent)
        finally:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            if temporary:
                try:
                    os.remove(temporary)
                except OSError:
                    pass


    def new_file(self):
        if not self.check_save_changes(): return False
        self._loading=True
        try:
            self.clear_search_results(); self.visual_editor.clear(); self.file_path=None; self.file_format="rtf"; self.file_encoding="rtf"; self.file_bom=b""; self.file_newline="\n"; self.file_disk_signature=None; self._source_rtf_payload=None; self._source_rtf_semantic_signature=None; self.content_saved=True; self.rtf_compatibility_warnings=(); self.rtf_document_properties={}; self._rtf_save_warning_acknowledged=False; self._view_only_prompt_shown=False; self._visual_document_zoom_percent=100; self.apply_editor_font(); self._apply_visual_document_zoom(self.zoom_percent); self.visual_editor.document().setModified(False)
        finally: self._loading=False
        self._set_external_change_pending(False); self._rebind_file_watcher(None)
        self.view_only=bool(self.persist_view_only); self._update_mode_capabilities(); self.update_title(); self.update_status_counts(); self.update_formatting_state(); self.visual_editor.setFocus(); return True


    def save_and_exit(self):
        """Offer save-and-exit, exit-without-saving, or cancel explicitly."""
        self._refresh_backing_state_from_disk()
        if self._backing_state == "missing":
            if not self._confirm_missing_backing_preservation():
                return False
            self._skip_close_save_prompt = True
            self.close()
            return True
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setWindowTitle("Save and Exit — RiqatonyPad")
        dialog.setText("Do you want to save the current document before exiting RiqatonyPad?")
        save_button = dialog.addButton(
            "Yes, save and exit", QMessageBox.ButtonRole.AcceptRole
        )
        discard_button = dialog.addButton(
            "No, exit without saving", QMessageBox.ButtonRole.DestructiveRole
        )
        cancel_button = dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(cancel_button)
        dialog.setEscapeButton(cancel_button)
        dialog.exec()

        clicked = dialog.clickedButton()
        if clicked is cancel_button or clicked is None:
            return False
        if clicked is save_button:
            if not self.save_file():
                return False
        elif clicked is not discard_button:
            return False

        self._skip_close_save_prompt = True
        self.close()
        return True


    def open_file(self):
        if not self.check_save_changes(): return
        file_path,_=QFileDialog.getOpenFileName(self,"Open RTF Document — RiqatonyPad","","Rich Text Format (*.rtf);;All Files (*)")
        if file_path: self.load_file(file_path,check_changes=False)


    @staticmethod
    def inspect_text_file(file_path):
        try:
            if not os.path.isfile(file_path): return False,"The selected path is not a regular file."
            size=os.path.getsize(file_path)
            if size>MAX_FILE_SIZE: return False,f"The file is larger than RiqatonyPad's {MAX_FILE_SIZE//(1024*1024)} MiB safety limit."
        except OSError as exc: return False,f"Could not inspect the file:\n{exc}"
        if Path(file_path).suffix.lower() not in RTF_EXTENSIONS: return False,"RiqatonyPad 1.1.2 edits Rich Text Format (.rtf) documents only."
        return True,""


    def load_file(self, file_path, check_changes=True, show_error=True):
        if check_changes and not self.check_save_changes(): return False
        is_safe,reason=self.inspect_text_file(file_path)
        if not is_safe:
            if show_error: QMessageBox.information(self,"Unsupported File — RiqatonyPad",f"RiqatonyPad did not open:\n{os.path.basename(file_path)}\n\n{reason}")
            return False
        try:
            data=read_bounded_bytes(file_path,MAX_FILE_SIZE,label="document"); decoded=decode_rtf(data)
        except (ValueError,MemoryError,OSError) as exc:
            if show_error: QMessageBox.warning(self,"RTF Import Error — RiqatonyPad",f"The RTF document could not be opened safely:\n{exc}")
            return False
        except Exception as exc:
            if show_error: QMessageBox.critical(self,"RTF Import Error — RiqatonyPad",f"RiqatonyPad could not import this RTF document:\n{exc}")
            return False
        self._loading=True
        try:
            self.clear_search_results()
            direct_import = populate_qtextdocument_from_rtf_model(
                self.visual_editor.document(), decoded.model
            )
            if not direct_import:
                # Conservative table fallback.  Ordinary paragraphs, blank blocks,
                # indentation and embedded-image provenance no longer pass through
                # Qt's lossy HTML normalization layer.
                document_html=sanitise_qt_html(decoded.html)
                self.visual_editor.setHtml(document_html)
                if decoded.automatic_foreground:
                    _rtf_clear_automatic_foreground(self.visual_editor.document(),decoded.automatic_foreground)
            self.apply_editor_canvas_theme(update_action=True); self._visual_document_zoom_percent=100; self._apply_visual_document_zoom(self.zoom_percent); self.visual_editor.document().clearUndoRedoStacks(); self.visual_editor.document().setModified(False)
            self.file_path=os.path.abspath(file_path); self.file_format="rtf"; self.file_encoding="rtf"; self.file_bom=b""; self.file_newline="\n"; self.file_disk_signature=self._content_signature(data); self._source_rtf_payload=bytes(data); self.content_saved=True; self.rtf_compatibility_warnings=tuple(decoded.warnings); self.rtf_document_properties=dict(decoded.document_properties); self._rtf_save_warning_acknowledged=False; self.view_only=bool(self.persist_view_only); self._view_only_prompt_shown=False
            try:
                self._source_rtf_semantic_signature=self._content_signature(self._document_payload("rtf"))
            except Exception:
                self._source_rtf_semantic_signature=None
        finally: self._loading=False
        self._set_external_change_pending(False); self._rebind_file_watcher(self.file_path)
        self._update_mode_capabilities(); self.update_title(); self.update_status_counts(); self.update_formatting_state(); self.visual_editor.setFocus()
        if self.rtf_compatibility_warnings: self._show_status_message("RTF opened with compatibility warnings. Review File → More Actions → Properties before saving.",7000)
        else: self._show_status_message(f"Loaded {os.path.basename(self.file_path)}", 3000)
        return True


    @staticmethod
    def _default_created_file_mode():
        """Return the normal 0666 mode after applying the process umask."""
        current_umask = os.umask(0)
        os.umask(current_umask)
        return 0o666 & ~current_umask


    def save_file(self, check_external_change=True):
        if not self.file_path: return self.save_as_file()
        if check_external_change:
            action=self._external_change_action()
            if action=="reload": self._reload_external_change(); return False
            if action=="save_version_as": return self._save_version_as()
            if action!="overwrite": return False
        document_dirty = (not self.content_saved) or self.visual_editor.document().isModified()
        canonical_payload = None
        canonical_signature = None
        semantically_clean = False
        if (
            document_dirty
            and self._source_rtf_payload is not None
            and self._source_rtf_semantic_signature is not None
        ):
            try:
                canonical_payload = self._document_payload("rtf")
                canonical_signature = self._content_signature(canonical_payload)
                semantically_clean = canonical_signature == self._source_rtf_semantic_signature
            except (ValueError, RuntimeError, MemoryError):
                canonical_payload = None
                canonical_signature = None
                semantically_clean = False
        clean_source = (
            self._source_rtf_payload is not None
            and ((not document_dirty) or semantically_clean)
        )
        if (
            clean_source
            and self.file_disk_signature == self._content_signature(self._source_rtf_payload)
            and self._disk_signature(self.file_path) == self.file_disk_signature
        ):
            # A plain Save on an unchanged loaded document is deliberately a
            # no-op.  A net-zero edit (type/delete back to the loaded supported
            # semantics) is treated the same way, so foreign RTF scaffolding is
            # not destroyed merely because Qt's modified flag stayed sticky.
            self._synchronise_after_save(
                self._source_rtf_payload,
                semantic_signature=self._source_rtf_semantic_signature,
                preserve_warnings=True,
            )
            self.content_saved=True
            self._set_external_change_pending(False)
            self._rebind_file_watcher(self.file_path)
            self._update_mode_capabilities(); self.update_title(); self.update_status_counts()
            self._show_status_message(f"Saved {os.path.basename(self.file_path)}.", 4000)
            return True
        if (not clean_source) and self.rtf_compatibility_warnings and not self._rtf_save_warning_acknowledged:
            details="\n• ".join(self.rtf_compatibility_warnings)
            box=QMessageBox(self); box.setIcon(QMessageBox.Icon.Warning); box.setWindowTitle("RTF Compatibility Warning — RiqatonyPad"); box.setText("This document contains RTF constructs that RiqatonyPad does not fully preserve."); box.setInformativeText("Saving will rewrite the document using RiqatonyPad's supported RTF subset. The following content may be discarded:\n\n• "+details+"\n\nContinue only if that is acceptable."); save_btn=box.addButton("Save Supported Content",QMessageBox.ButtonRole.AcceptRole); box.addButton(QMessageBox.StandardButton.Cancel); box.exec()
            if box.clickedButton() is not save_btn: return False
            self._rtf_save_warning_acknowledged=True
        try:
            if clean_source:
                payload=bytes(self._source_rtf_payload)
                semantic_signature=self._source_rtf_semantic_signature
            else:
                payload=canonical_payload if canonical_payload is not None else self._document_payload("rtf")
                semantic_signature=canonical_signature or self._content_signature(payload)
            if len(payload)>MAX_FILE_SIZE: raise ValueError(f"The saved document would exceed RiqatonyPad's {MAX_FILE_SIZE//(1024*1024)} MiB reopen limit.")
            self._write_payload_atomically(payload); self.file_disk_signature=self._content_signature(payload); self._synchronise_after_save(payload, semantic_signature=semantic_signature, preserve_warnings=clean_source); self.content_saved=True; self._set_external_change_pending(False); self._rebind_file_watcher(self.file_path); self._update_mode_capabilities(); self.update_title(); self.update_status_counts()
            self._show_status_message(f"Saved {os.path.basename(self.file_path)}.", 4000)
            return True
        except MemoryError: QMessageBox.critical(self,"Save Error","The document is too large to encode safely. No changes were written.")
        except (OSError,ValueError,RuntimeError) as exc: QMessageBox.critical(self,"Save Error",f"Could not save the document:\n{exc}")
        except Exception as exc: QMessageBox.critical(self,"Save Error",f"RiqatonyPad could not serialise this document safely:\n{exc}")
        return False


    def rename_current_file(self):
        if not self.file_path:
            QMessageBox.information(self, "Rename", "This document has not been saved yet. Use Save As to give it a name.")
            return False
        if self._document_is_dirty():
            if not self.check_save_changes():
                return False
            if self._document_is_dirty():
                # The user chose Discard. Rebind the live editor to the disk copy
                # before changing its path so discarded text cannot follow the rename.
                if not self.load_file(self.file_path, check_changes=False, show_error=True):
                    return False

        old_path = os.path.abspath(self.file_path)
        expected_identity = self._path_identity(old_path)
        expected_signature = self._disk_signature(old_path)
        if expected_identity is None or expected_signature is None:
            QMessageBox.warning(self, "Rename Cancelled", "The file is no longer available.")
            return False
        if self.file_disk_signature is not None and expected_signature != self.file_disk_signature:
            self._set_external_change_pending(True)
            QMessageBox.warning(
                self, "Rename Cancelled",
                "The file changed outside RiqatonyPad. Review the external version before renaming it.",
            )
            return False

        old_name = os.path.basename(old_path)
        parent_dir = os.path.dirname(old_path)
        new_name, accepted = QInputDialog.getText(
            self, "Rename", "New filename:", QLineEdit.EchoMode.Normal, old_name
        )
        if not accepted:
            return False
        new_name = new_name.strip()
        if not new_name or os.path.basename(new_name) != new_name or new_name in (".", ".."):
            QMessageBox.warning(self, "Rename", "Enter a filename only, without a folder path.")
            return False
        if not Path(new_name).suffix:
            new_name += ".rtf"
        new_path = os.path.abspath(os.path.join(parent_dir, new_name))
        if new_path == old_path:
            return True
        if self.format_for_path(new_path) != self.file_format:
            QMessageBox.warning(self, "Rename", "Rename cannot change the document format. Use Save As to convert it.")
            return False
        if os.path.lexists(new_path):
            QMessageBox.warning(
                self, "Rename Cancelled",
                f'A file named "{os.path.basename(new_path)}" already exists. Choose another name.',
            )
            return False
        if self._path_identity(old_path) != expected_identity or self._disk_signature(old_path) != expected_signature:
            QMessageBox.warning(
                self, "Rename Cancelled",
                "The file changed or was replaced while the rename dialog was open. Nothing was renamed.",
            )
            return False
        try:
            self._rename_path_no_replace(old_path, new_path)
            fsync_directory(parent_dir or os.curdir)
        except (OSError, RuntimeError) as exc:
            QMessageBox.critical(self, "Rename Failed", f"RiqatonyPad could not rename the file.\n\n{exc}")
            return False
        self.file_path = new_path
        self.file_disk_signature = self._disk_signature(new_path)
        self._set_external_change_pending(False)
        self._rebind_file_watcher(new_path)
        self._update_mode_capabilities()
        self.update_title()
        self.update_status_counts()
        self._show_status_message(f"Renamed {old_name} to {os.path.basename(new_path)}.", 4000)
        return True


    def save_as_file(
        self,
        *,
        initial_path=None,
        forbidden_paths=(),
        dialog_title="Save As — RiqatonyPad",
        forbidden_message=None,
    ):
        # During an unresolved external-change conflict, ordinary Save As is a
        # preservation operation. Only the explicit Overwrite choice in the
        # Save conflict dialog may replace the changed source file.
        if not forbidden_paths and self._has_external_change():
            self._set_external_change_pending(True)
            return self._save_version_as()
        if self._external_change_pending and not self._has_external_change():
            self._set_external_change_pending(False)
        initial_path = initial_path or self.file_path or os.path.join(os.path.expanduser("~"), "Untitled.rtf")
        file_path, _ = QFileDialog.getSaveFileName(self, dialog_title, initial_path, "Rich Text Format (*.rtf)")
        if not file_path:
            return False
        if not Path(file_path).suffix:
            file_path += ".rtf"
        if Path(file_path).suffix.lower() not in RTF_EXTENSIONS:
            QMessageBox.warning(self, "Unsupported Extension — RiqatonyPad", "RiqatonyPad 1.1.2 saves .rtf documents only.")
            return False
        candidate = Path(file_path).expanduser().resolve(strict=False)
        forbidden = {Path(path).expanduser().resolve(strict=False) for path in forbidden_paths}
        if candidate in forbidden:
            QMessageBox.warning(
                self,
                dialog_title,
                forbidden_message or "Choose a different filename for this version.",
            )
            return False

        old_path = os.path.abspath(self.file_path) if self.file_path else ""
        target_path = os.path.abspath(file_path)
        if old_path and target_path == old_path:
            if self._has_external_change():
                self._set_external_change_pending(True)
                return self._save_version_as()
            return self.save_file(check_external_change=False)

        document_dirty = self._document_is_dirty()
        canonical_payload = None
        canonical_signature = None
        semantically_clean = False
        if (
            document_dirty
            and self._source_rtf_payload is not None
            and self._source_rtf_semantic_signature is not None
        ):
            try:
                canonical_payload = self._document_payload("rtf")
                canonical_signature = self._content_signature(canonical_payload)
                semantically_clean = canonical_signature == self._source_rtf_semantic_signature
            except (ValueError, RuntimeError, MemoryError):
                canonical_payload = None
                canonical_signature = None
                semantically_clean = False
        clean_source = self._source_rtf_payload is not None and ((not document_dirty) or semantically_clean)
        if (not clean_source) and self.rtf_compatibility_warnings and not self._rtf_save_warning_acknowledged:
            details = "\n• ".join(self.rtf_compatibility_warnings)
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setWindowTitle("RTF Compatibility Warning — RiqatonyPad")
            box.setText("This document contains RTF constructs that RiqatonyPad does not fully preserve.")
            box.setInformativeText(
                "Saving will rewrite the document using RiqatonyPad's supported RTF subset. "
                "The following content may be discarded:\n\n• " + details +
                "\n\nContinue only if that is acceptable."
            )
            save_btn = box.addButton("Save Supported Content", QMessageBox.ButtonRole.AcceptRole)
            box.addButton(QMessageBox.StandardButton.Cancel)
            box.exec()
            if box.clickedButton() is not save_btn:
                return False
            self._rtf_save_warning_acknowledged = True

        try:
            if clean_source:
                payload = bytes(self._source_rtf_payload)
                semantic_signature = self._source_rtf_semantic_signature
            else:
                payload = canonical_payload if canonical_payload is not None else self._document_payload("rtf")
                semantic_signature = canonical_signature or self._content_signature(payload)
            if len(payload) > MAX_FILE_SIZE:
                raise ValueError(
                    f"The saved document would exceed RiqatonyPad's {MAX_FILE_SIZE//(1024*1024)} MiB reopen limit."
                )

            # Transactional Save As: write the target while the live editor still
            # belongs to the source path. Only a successful independent write
            # may change the current document identity.
            self._write_payload_atomically(payload, target_path=target_path)

            self.file_path = target_path
            self.file_format = "rtf"
            self.file_encoding = "rtf"
            self.file_bom = b""
            self.file_newline = "\n"
            self.file_disk_signature = self._content_signature(payload)
            self._set_external_change_pending(False)
            self._rebind_file_watcher(target_path)
            self._synchronise_after_save(
                payload,
                semantic_signature=semantic_signature,
                preserve_warnings=clean_source,
            )
            self.content_saved = True
            self._update_mode_capabilities()
            self.update_title()
            self.update_status_counts()
            if not forbidden_paths:
                self._show_status_message(f"Saved as {os.path.basename(target_path)}", 3000)
            return True
        except MemoryError:
            QMessageBox.critical(self, "Save Error", "The document is too large to encode safely. No changes were written.")
        except (OSError, ValueError, RuntimeError) as exc:
            QMessageBox.critical(self, "Save Error", f"Could not save the document:\n{exc}")
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", f"RiqatonyPad could not serialise this document safely:\n{exc}")
        return False


    def open_dropped_files(self, files):
        files = [os.path.abspath(path) for path in files if os.path.isfile(path)]
        if not files:
            return
        accepted = []
        rejected = []
        for path in files:
            is_document, reason = self.inspect_text_file(path)
            if is_document:
                accepted.append(path)
            else:
                rejected.append((path, reason))
        if rejected:
            names = "\n".join(f"• {os.path.basename(path)}" for path, _ in rejected[:10])
            if len(rejected) > 10:
                names += f"\n• …and {len(rejected) - 10} more"
            QMessageBox.warning(
                self, "Unsupported Files Skipped",
                "RiqatonyPad skipped unsupported or unsafe files:\n\n" + names,
            )
        if not accepted:
            return
        if self.drop_open_mode == "new_window":
            for path in accepted:
                self.new_window(path)
            return
        if not self.check_save_changes():
            return
        first, *rest = accepted
        if self.load_file(first, check_changes=False):
            for path in rest:
                self.new_window(path)

