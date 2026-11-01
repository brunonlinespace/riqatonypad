#!/usr/bin/env python3
"""x13.4: precise backing-warning identity and predecessor code-preservation gate."""
from __future__ import annotations
import ast
import hashlib
import json
import sys
from pathlib import Path
from types import MethodType

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
contract = json.loads((ROOT / 'qa/x134-preservation.json').read_text())
assert contract['predecessor'] == '2.0.0-x13.3'
assert contract['release'] == '2.0.0-x13.4'
for rel, digest in contract['untouched_production_files'].items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() == digest, rel
for rel, methods in contract['unchanged_methods'].items():
    tree = ast.parse((ROOT/rel).read_text())
    current = {
        cls.name+'.'+method.name: hashlib.sha256(ast.dump(method, include_attributes=False).encode()).hexdigest()
        for cls in tree.body if isinstance(cls, ast.ClassDef)
        for method in cls.body if isinstance(method, (ast.FunctionDef,ast.AsyncFunctionDef))
    }
    for name, expected in methods.items():
        assert current[name] == expected, (rel,name)
    assert set(current)==(set(methods)|set(contract['modified_methods'][rel])), rel


def extract(relative_file, class_name, method_name):
    tree = ast.parse((ROOT/relative_file).read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name==class_name)
    fn = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name==method_name)
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])), '<x134-method>', 'exec'), namespace)
    return namespace[method_name]

clear = extract('app.py','RiqatonyPad','_clear_status_message')
show = extract('app.py','RiqatonyPad','_show_status_message')
set_state = extract('widgets/rwpyn/editor_lifecycle.py','EditorFileLifecycleMixin','_set_backing_state')
watch = extract('widgets/rwpyn/editor_lifecycle.py','EditorFileLifecycleMixin','_check_external_change_from_watcher')

class Label:
    def __init__(self): self.text='';self.tooltip='';self.visible=False;self.enabled=True
    def setText(self,text): self.text=text
    def setToolTip(self,text): self.tooltip=text
    def clear(self): self.text=''
    def show(self): self.visible=True
    def hide(self): self.visible=False
    def setEnabled(self,enabled): self.enabled=enabled

class Timer:
    def __init__(self): self.started=[];self.stopped=0
    def start(self,ms): self.started.append(ms)
    def stop(self): self.stopped+=1

class Surface:
    def __init__(self):
        self.status_message_label=Label()
        self._status_message_timer=Timer()
        self.external_banner=Label()
        self.external_label=Label()
        self.external_reload_button=Label()
        self._backing_state='normal'
        self._critical_editor_message=False
        self._critical_editor_message_kind=None
        self._external_change_pending=False
        self._expected_delete_message=False
        self.file_path='/sample/file.rtf'
        self.file_disk_signature='original'
        self.disk_signature='original'
    _show_status_message=show
    _clear_status_message=clear
    _set_backing_state=set_state
    _check_external_change_from_watcher=watch
    def _disk_signature(self,_file_path): return self.disk_signature
    def _rebind_file_watcher(self,_file_path): pass

# Both real watcher warnings must be tagged, persistent, and clear when the
# original backing bytes reappear.
for disk_state, warning_prefix in ((None,'Backing file missing;'),('externally-edited','File changed outside')):
    surface=Surface()
    surface.disk_signature=disk_state
    surface._check_external_change_from_watcher()
    assert surface._critical_editor_message
    assert surface._critical_editor_message_kind=='backing'
    assert surface.status_message_label.text.startswith(warning_prefix)
    assert surface.external_banner.visible
    assert surface._status_message_timer.started == []  # persistent
    surface._check_external_change_from_watcher()
    assert surface._critical_editor_message  # still unresolved
    surface.disk_signature='original'
    surface._check_external_change_from_watcher()
    assert not surface._critical_editor_message
    assert surface._critical_editor_message_kind is None
    assert surface.status_message_label.text==''
    assert not surface.external_banner.visible
    assert not surface._external_change_pending

# A restored backing path must NOT clear any other critical message.
for warning in (
    'RTF opened with compatibility warnings. Review Properties before saving.',
    'Could not load example.rtf.',
    'Could not save example.rtf.',
):
    surface=Surface()
    surface._show_status_message(warning,7000)
    assert surface._critical_editor_message and surface._critical_editor_message_kind is None
    surface._set_backing_state('missing')
    surface._set_backing_state('normal')
    assert surface._critical_editor_message
    assert surface.status_message_label.text==warning
    assert not surface._status_message_timer.started

# Unresolved warnings still suppress routine messages; successful recovery
# confirmations retain x13.3's preexisting priority and four-second timing.
surface=Surface()
surface._show_status_message('File changed outside RiqatonyPad.',5000,warning_kind='backing')
surface._show_status_message('Ordinary work completed.',2000)
assert surface.status_message_label.text=='File changed outside RiqatonyPad.'
surface._show_status_message('Saved example.rtf',2500)
assert surface.status_message_label.text=='Saved example.rtf.'
assert surface._critical_editor_message is False
assert surface._critical_editor_message_kind is None
assert surface._status_message_timer.started==[4000]
surface._clear_status_message()
assert surface._critical_editor_message_kind is None
assert surface.status_message_label.text==''

# The new explicit provenance parameter must not affect critical detection or
# the old status presentation defaults.
surface=Surface()
surface._show_status_message('Backing file missing; preserve this document.',6000)
assert surface._critical_editor_message and surface._critical_editor_message_kind is None
surface._set_backing_state('normal')
assert surface.status_message_label.text.startswith('Backing file missing;')

print('PASS: x13.4 precise warning identity, watcher events, priority, and unchanged-method hashes')
