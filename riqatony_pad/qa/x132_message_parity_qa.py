#!/usr/bin/env python3
"""x13.2 scope and delivery regression: eight approved message additions only."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,json,os,tempfile

root=Path(__file__).resolve().parents[1]
contract=json.loads((root/'qa/x132_message_contract.json').read_text())
assert contract['current_version']=='2.0.0-x13.2'
for name,record in contract['allowed_edits'].items():
    text=(root/name).read_text(encoding='utf-8')
    for change in reversed(record['replacements']):
        added=change['released']; replaced=change['previous']
        assert text.count(added)==1, (name,'approved hunk missing/modified')
        text=text.replace(added,replaced,1)
    assert hashlib.sha256(text.encode()).hexdigest()==record['x131_sha256'], (name,'non-approved production change')
for name,digest in contract['other_production_files'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest, ('unapproved production module modified',name)
for name in ('app.py','widgets/rwpyn/editor_lifecycle.py','widgets/rwpyn/editor_insertion.py'):
    ast.parse((root/name).read_text(encoding='utf-8'))

app=(root/'app.py').read_text(); life=(root/'widgets/rwpyn/editor_lifecycle.py').read_text(); insertion=(root/'widgets/rwpyn/editor_insertion.py').read_text()
assert app.count('self._show_status_message("Overwrite mode enabled." if editor.overwriteMode() else "Insert mode enabled.", 2500)')==1
assert 'self.status_message_label.setToolTip(text)' in app
assert 'addPermanentWidget(self.status_indicators_label)' in app
assert life.count('self._show_status_message("Saved.", 2500)')==2
assert 'if self.rtf_compatibility_warnings: self._show_status_message(' in life
assert 'else: self._show_status_message(f"Loaded {os.path.basename(self.file_path)}", 3000)' in life
assert 'if not forbidden_paths:\n                self._show_status_message(f"Saved as {os.path.basename(target_path)}", 3000)' in life
assert 'self._show_status_message(f"Renamed {old_name} to {os.path.basename(new_path)}", 3000)' in life
assert 'self._show_status_message("Clipboard does not contain text that can be pasted.", 3500)' in insertion
assert 'self._show_status_message(f"Opened {os.path.basename(self.file_path)} in an external editor.", 3000)' in life
assert 'self._show_status_message(f"Opened the folder containing {os.path.basename(self.file_path)}.", 3000)' in life
assert 'self._show_status_message(' not in life[life.index('        if not file_path:\n            return False',life.index('    def save_as_file(')):life.index('        if not Path(file_path).suffix:',life.index('    def save_as_file('))]

# Execute the real (unmodified) methods with minimal stubs, proving message
# destinations and success/failure gating without requiring Fedora/PyQt6.
def method(file,name):
    tree=ast.parse((root/file).read_text())
    defs=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name]
    assert len(defs)==1,(file,name)
    node=defs[0]; node.decorator_list=[]
    namespace={'os':os}
    class MessageBox:
        class _R: pass
        @staticmethod
        def warning(*args):return None
    namespace['QMessageBox']=MessageBox
    namespace['QApplication']=SimpleNamespace(clipboard=lambda:SimpleNamespace(text=lambda:''))
    ns=namespace.copy()
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),file,'exec'),ns)
    return ns[name]

external=method('widgets/rwpyn/editor_lifecycle.py','open_external_editor')
folder=method('widgets/rwpyn/editor_lifecycle.py','open_containing_folder')
messages=[]
test_dir=tempfile.TemporaryDirectory()
(Path(test_dir.name)/'hello.rtf').write_text('{\\rtf1\\ansi}')
owner=SimpleNamespace(file_path=str(Path(test_dir.name)/'hello.rtf'), _document_is_dirty=lambda:False, dirty_external_action='ask', _open_host_target=lambda *a,**k:True, _show_status_message=lambda msg,t:messages.append((msg,t)))
assert external(owner)==True and messages==[('Opened hello.rtf in an external editor.',3000)],messages
messages.clear()
assert folder(owner)==True and messages==[('Opened the folder containing hello.rtf.',3000)],messages
messages.clear();owner._open_host_target=lambda *a,**kw:False
assert external(owner)==False and messages==[],messages
assert folder(owner)==False and messages==[],messages
test_dir.cleanup()

plain=method('widgets/rwpyn/editor_insertion.py','paste_plain_text')
messages.clear()
owner=SimpleNamespace(document_editing_available=lambda:True,_show_status_message=lambda msg,t:messages.append((msg,t)))
plain(owner)
assert messages==[('Clipboard does not contain text that can be pasted.',3500)],messages

# Confirm full successful-load branch ordering remains intact; warning wins.
load=next(n for n in ast.walk(ast.parse(life)) if isinstance(n,ast.FunctionDef) and n.name=='load_file')
assert isinstance(load.body[-2],ast.If) and isinstance(load.body[-1],ast.Return)
assert isinstance(load.body[-2].orelse[0],ast.Expr), 'loaded feedback must be the compatibility-warning alternative'

print('PASS: x13.2 exact x13.1 production preservation and all eight approved feedback paths')
