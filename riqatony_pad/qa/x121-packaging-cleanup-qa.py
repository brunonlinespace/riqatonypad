#!/usr/bin/env python3
"""x12.1 bounded cleanup: no obsolete documentation, canonical Windows location and README protection."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
OUTER=ROOT.parent
VERSION='2.0.0-x13.0'
ORIG='2.0.0-x12.0'
def sha(b): return hashlib.sha256(b).hexdigest()
assert not (ROOT/'OFFICIAL_SOURCE.md').exists(), 'obsolete provenance file remains'
assert not (ROOT/'windows').exists(), 'old Windows build folder remains'
WIN=ROOT/'packaging'/'windows'
assert WIN.is_dir()
for name in ('README.md','build-requirements.txt','build-windows-portable.ps1','windows-version-info.txt'):
    assert (WIN/name).is_file(), f'missing Windows file: {name}'
builder=(WIN/'build-windows-portable.ps1').read_text(encoding='utf-8')
assert "..\\.." in builder, 'builder root path not updated'
assert VERSION in builder
assert sha((OUTER/'README.md').read_bytes().replace(VERSION.encode(),ORIG.encode()))=='cae48c68048f788a396c630ec049c8a3b1dfa0452ba8e703a8b3a65e0ff19b28', 'public GitHub README altered beyond current version'
assert sha((ROOT/'README.md').read_bytes().replace(VERSION.encode(),ORIG.encode()))=='c1b545d39d8a64faae42a90a4558c37f3b37e199c4cb1516bb932fc364bd4c13', 'internal README altered beyond current version'
manifest=(ROOT/'SOURCE_MANIFEST.sha256').read_text(encoding='utf-8')
assert 'OFFICIAL_SOURCE.md' not in manifest
assert '/windows/build-windows-portable.ps1' in manifest
assert "./windows/" not in manifest
# Pin all four Windows packaging files to their issued x12.0 contents,
# allowing only the approved version literal and application-root relocation.
BASELINE_WINDOWS = {'README.md': '08f7db10607000d26212486865247dc67bc30cccb2b514631001844e89cf0925', 'build-requirements.txt': 'a2749454cf131466b9abc5fe2693d1bd7e0d6c1d34943dfdc6ab942c036a6aee', 'windows-version-info.txt': '05c9f06f03e7d1d2a0a2f95c3a46f6e39004c52915c9075045520e500a91c53d', 'build-windows-portable.ps1': '2898ae2a5ed46b4baf94409e5a6be8f25653c758e4f604191dd828a76926b26f'}
for name in BASELINE_WINDOWS:
    current=(WIN/name).read_bytes()
    if name in ('windows-version-info.txt','build-windows-portable.ps1'):
        current=current.replace(VERSION.encode(),ORIG.encode())
    if name=='build-windows-portable.ps1':
        # x12.5 adds only the two explicitly staged dialog modules.
        # The x12.5 release gate independently requires these four lines.
        current=b''.join(line for line in current.splitlines(keepends=True)
            if not (b'$AboutDialog = Join-Path ' in line or b'$QuickTour = Join-Path ' in line
                    or b'Copy-Item -LiteralPath $AboutDialog -Destination ' in line
                    or b'Copy-Item -LiteralPath $QuickTour -Destination ' in line))
        current=current.replace(b'widgets/keyboard_shortcuts.py',b'widgets/shortcut_search.py')
    if name=='build-windows-portable.ps1':
        # x12.3 changes only source/stage paths and adds package initialisers.
        # Restore the x12.1 path spelling before checking the frozen x12.0 hash.
        import re
        current=b''.join(line for line in current.splitlines(keepends=True)
                         if not (line.startswith(b'New-Item -ItemType Directory -Path (Join-Path $Stage "widgets\\rwpyn")')
                                 or (line.startswith(b'Copy-Item -LiteralPath (Join-Path $Root "widgets\\') and b'__init__.py' in line)))
        current=re.sub(rb'widgets/(?:rwpyn/)?(?=editor_[a-z_]+\.py)', b'', current)
        current=current.replace(b'widgets/shortcut_search.py', b'shortcut_search.py')
        current=current.replace(b'$Root = (Resolve-Path (Join-Path $ScriptDir "..\\..")).Path',b'$Root = Split-Path -Parent $ScriptDir')
    assert sha(current)==BASELINE_WINDOWS[name], f'unapproved Windows file changes: {name}'
print('PASS: x12.1 Windows/provenance cleanup and README preservation')
