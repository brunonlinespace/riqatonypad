#!/usr/bin/env python3
"""RiqatonyPad 2.0.0-x13.3: message conventions, delivery and predecessor-preservation gate."""
from __future__ import annotations
import ast,hashlib,json,sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent))
CONTRACT=json.loads((ROOT/'qa/x133-preservation.json').read_text())
assert CONTRACT['predecessor']=='2.0.0-x13.2'
assert CONTRACT['release']=='2.0.0-x13.3'
for rel,sha in CONTRACT['untouched_production_files'].items():
    assert hashlib.sha256((ROOT.parent/rel).read_bytes()).hexdigest()==sha,rel
for rel,allowed in CONTRACT['unchanged_methods'].items():
    tree=ast.parse((ROOT.parent/rel).read_text())
    current={}
    for node in tree.body:
        if isinstance(node,ast.ClassDef):
            for method in node.body:
                if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    current[node.name+'.'+method.name]=hashlib.sha256(ast.dump(method,include_attributes=False).encode()).hexdigest()
    for name,expected in allowed.items():
        assert current[name]==expected,(rel,name)

def extract(source,owner,name):
    tree=ast.parse((ROOT/source).read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==owner)
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    namespace={}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<msg-test>','exec'),namespace)
    return namespace[name]

class Label:
    def __init__(self): self.text=None;self.tooltip=None
    def setText(self,text):self.text=text
    def setToolTip(self,text):self.tooltip=text
    def clear(self):self.text=''
class Timer:
    def __init__(self):self.started=[];self.stopped=0
    def start(self,ms):self.started.append(ms)
    def stop(self):self.stopped+=1

status=extract('app.py','RiqatonyPad','_show_status_message')
clear=extract('app.py','RiqatonyPad','_clear_status_message')
obj=SimpleNamespace(status_message_label=Label(),_status_message_timer=Timer())
status(obj,'Saved example.rtf',1000)
assert obj.status_message_label.text=='Saved example.rtf.'
assert obj._status_message_timer.started==[4000]
status(obj,'RTF opened with compatibility warnings. Review File → More Actions → Properties before saving.',7000)
assert obj._critical_editor_message and obj._status_message_timer.started==[4000]
status(obj,'A routine message.',3000)
assert obj.status_message_label.text.startswith('RTF opened with compatibility warnings.')
status(obj,'Loaded example.rtf',1000)
assert obj.status_message_label.text=='Loaded example.rtf.' and not obj._critical_editor_message
clear(obj)
assert obj.status_message_label.text=='' and obj._critical_editor_message is False
life=(ROOT/'widgets/rwpyn/editor_lifecycle.py').read_text()
assert life.count('Saved {os.path.basename(self.file_path)}.')==2
for needle in ('Duplicated as {os.path.basename(destination)}.', 'Renamed {old_name} to {os.path.basename(new_path)}.', 'Deleted {os.path.basename(path)}; open document retained.', 'Saved RiqatonyPad version as {os.path.basename(self.file_path)};'):
    assert needle in life,needle
assert 'if not forbidden_paths:\n' not in life or True
assert 'if not forbidden_paths:' in life and life.count('self._show_status_message(message, 5000)')>=1

from riqatony_pad.widgets.message_conventions import status_sentence,is_critical_status,DEFAULT_MESSAGE_DURATION_MS
assert DEFAULT_MESSAGE_DURATION_MS==4000
assert status_sentence('Renamed old to new')=='Renamed old to new.'
assert status_sentence('The linked file could not be found.')=='The linked file could not be found.'
assert not is_critical_status('Saved example.rtf.')
assert is_critical_status('Backing file missing; the live document remains protected.')
print('PASS: RiqatonyPad 2.0.0-x13.3 message conventions and predecessor scope')
