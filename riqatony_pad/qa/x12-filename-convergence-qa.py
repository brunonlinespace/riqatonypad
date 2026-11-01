#!/usr/bin/env python3
"""x12 canonical app-module relocation: pinned source text, launch and history contract."""
from __future__ import annotations
import ast, hashlib, json, re, stat
from pathlib import Path
from source_contract import contract_text
OLD_FILE='riqatonypad.py'
VERSION='2.0.0-x13.0'
PREVIOUS='2.0.0-x11.0'
HISTORY_MARKER=b'# RiqatonyPad 2.0.0-x11.0'
INTERNAL_MARKER=b'# RiqatonyPad 2.0.0-x11.0'
ROOT=Path(__file__).resolve().parents[1]
OUTER=ROOT.parent
GOLD=json.loads((ROOT/'qa/x12-filename-fingerprints.json').read_text())
assert (ROOT/'app.py').is_file()
assert not (ROOT/OLD_FILE).exists(), 'obsolete application module still present'
source=contract_text(ROOT)
lines=source.splitlines(keepends=True)
methods={}
def text_of(n):
    pos=min([n.lineno]+[d.lineno for d in n.decorator_list])-1
    return ''.join(lines[pos:n.end_lineno])
for node in ast.parse(source).body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
        methods['function:'+node.name]=hashlib.sha256(text_of(node).encode()).hexdigest()
    elif isinstance(node,ast.ClassDef):
        for method in node.body:
            if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)):
                methods['method:'+node.name+'.'+method.name]=hashlib.sha256(text_of(method).encode()).hexdigest()
assert methods==GOLD['methods'], 'original method source text changed after module relocation'
launcher=(OUTER/'main.py').read_text(encoding='utf-8')
assert 'entry_point = program_dir / "app.py"' in launcher
assert 'runpy.run_path(str(entry_point), run_name="__main__")' in launcher
assert 'APP_VERSION = "'+VERSION+'"' in source
assert bool((OUTER/'main.py').stat().st_mode & 0o111), 'main.py must be executable'
for relative in ('packaging/fedora/build-appimage.sh','packaging/windows/build-windows-portable.ps1'):
    script=(ROOT/relative).read_text(encoding='utf-8')
    assert 'app.py' in script and OLD_FILE not in script, relative
readme=(OUTER/'README.md').read_bytes().replace(VERSION.encode(),PREVIOUS.encode())
assert hashlib.sha256(readme).hexdigest()==GOLD['previous_root_readme_sha256'], 'GitHub root README changed beyond current version'
notes=(ROOT/'docs/RELEASE_NOTES.md').read_bytes()
changes=(ROOT/'docs/CHANGELOG.md').read_bytes()
# SHA256 of the predecessor's entire history, which must remain an unmodified suffix.
for data,key in ((notes,'previous_release_notes_sha256'),(changes,'previous_changelog_sha256')):
    marker=data.index(b'## 2.0.0-x11.0' if key=='previous_changelog_sha256' else HISTORY_MARKER)
    assert hashlib.sha256(data[marker:]).hexdigest()==GOLD[key], 'historical release records changed'
internal=(ROOT/'README.md').read_bytes()
assert hashlib.sha256(internal.replace(VERSION.encode(), PREVIOUS.encode())).hexdigest()==GOLD['previous_internal_readme_sha256'], 'internal README modified beyond current version'
print('PASS x12: canonical app.py, executable launcher, unchanged method source, preserved public README and history')
