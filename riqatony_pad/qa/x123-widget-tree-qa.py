#!/usr/bin/env python3
"""x12.3 standalone Pad widget-tree relocation and unchanged definitions."""
from pathlib import Path
import ast, hashlib, json, importlib.machinery
ROOT=Path(__file__).resolve().parents[1]
INFO=json.loads((ROOT/'qa/x123-widget-fingerprints.json').read_text())
assert INFO['baseline']=='2.0.0-x12.2' and INFO['version']=='2.0.0-x12.3'
assert (ROOT/'widgets/__init__.py').is_file()
assert (ROOT/'widgets/rwpyn/__init__.py').is_file()
assert not (ROOT/'widgets/editor').exists()
assert not (ROOT/'rwpyn').exists()
assert (ROOT/'app.py').is_file() and (ROOT/'editor_platform_startup.py').is_file()
for relative, expected in INFO['moved_definitions'].items():
    file=ROOT/relative
    assert file.is_file(),relative
    assert not (ROOT/file.name).exists(), 'obsolete duplicate module: '+file.name
    source=file.read_text()
    assert source.startswith('#!/usr/bin/env python3'),relative
    tree=ast.parse(source)
    lines=source.splitlines(keepends=True)
    got={}
    for n in tree.body:
        if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
            start=min([n.lineno]+[d.lineno for d in n.decorator_list])-1
            body=''.join(lines[start:n.end_lineno])
            if relative=='widgets/rwpyn/editor_preferences.py' and n.name=='resource_path':
                # Only approved environment shift: __file__ is now two levels lower.
                assert 'script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))' in body
                body=body.replace('script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))','script_dir = os.path.dirname(os.path.abspath(__file__))')
            got[n.name]=hashlib.sha256(body.encode()).hexdigest()
    assert got==expected,('definition drift',relative,expected.keys()^got.keys())
# Every internal moved-module import must resolve to an actual file.
old={name[:-3] for name in [*([x.name for x in ROOT.glob('editor_*.py')]),*([x.name for x in ROOT.glob('window_*.py')])]}
known={str(p.relative_to(ROOT)).replace('/','.')[:-3] for p in (ROOT/'widgets').rglob('*.py') if p.name!='__init__.py'}
for p in [ROOT/'app.py',ROOT/'editor_platform_startup.py',*(ROOT/'widgets').rglob('*.py')]:
    for node in ast.parse(p.read_text()).body:
        if isinstance(node,ast.ImportFrom) and node.module and node.module.startswith('widgets.'):
            assert node.module in known,(p,node.module)
        if isinstance(node,ast.Import):
            for alias in node.names:
                if alias.name.startswith('widgets.'):
                    assert alias.name in known,(p,alias.name)
assert all(p.read_text().startswith('#!/usr/bin/env python3') for p in ROOT.rglob('*.py'))
if 'riq'=='riq':
    preference=ROOT/'widgets/rwpyn/editor_preferences.py'
    assert 'script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))' in preference.read_text()
    builder=(ROOT/'packaging/fedora/build-appimage.sh').read_text()
    windows=(ROOT/'packaging/windows/build-windows-portable.ps1').read_text()
    for module in ('editor_widgets','editor_printing','editor_preferences','editor_lifecycle'):
        assert 'widgets/rwpyn/'+module+'.py' in builder and 'widgets/rwpyn/'+module+'.py' in windows
    assert 'widgets/__init__.py' in builder and 'widgets\\__init__.py' in windows
else:
    builder=(ROOT/'packaging/fedora/build-appimage.sh').read_text()
    for name in ('editor_source','editor_preview','editor_formatting','editor_insertion'):
        assert 'widgets/mwpyn/'+name+'.py' in builder
print('PASS x12.3: RiqatonyPad widget-tree relocation, exact original definitions, no obsolete modules and canonical build paths')
