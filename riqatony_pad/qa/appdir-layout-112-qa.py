#!/usr/bin/env python3
"""RiqatonyPad 1.1.2: verify the actual AppDir path contract of the Fedora builder.

This is an additive regression gate for the user-reproduced earlier 1.1.0 build failure;
it does not replace any inherited QA.
"""
from pathlib import Path
import re, tempfile, subprocess
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
script=(ROOT/'packaging/fedora/build-appimage.sh').read_text(encoding='utf-8')
# Require the destination of both document and LICENSE install statements to
# match the *created* documentation directory. Source folder remains underscored; AppDir uses the public application ID.
assert '\"$FINAL_APPDIR/usr/share/doc/riqatonypad\"' in script
assert '\"$FINAL_APPDIR/usr/share/doc/riqatonypad/${doc}\"' in script
assert '\"$FINAL_APPDIR/usr/share/doc/riqatonypad/LICENSE\"' in script
assert 'usr/share/doc/riqatony_pad/' not in script
# The PyInstaller payload stays under the executable/desktop ID, matching original Ricopad layout.
assert '\"$FINAL_APPDIR/usr/lib/riqatonypad\"' in script
assert '\"$FINAL_APPDIR/usr/lib/riqatonypad/\"' in script
assert 'usr/lib/riqatony_pad' not in script
assert '"doc" / "riqatonypad"' in contract_text(ROOT)
# Exercise the *real builder function* in a temporary mock PyInstaller tree,
# so source-only filename checks cannot conceal a missing destination directory.
import shlex
assembly=script.split('assemble_appdir() {',1)[1].split('\n}\n',1)[0]
assert 'install -m 0644' in assembly and 'validate_desktop_entry_basic' in assembly
with tempfile.TemporaryDirectory(prefix='riqatonypad-appdir-qa-') as td:
    t=Path(td)
    frozen=t/'pyinstaller'/'riqatonypad'; frozen.mkdir(parents=True)
    executable=frozen/'riqatonypad'
    executable.write_text('#!/bin/sh\nexit 0\n')
    executable.chmod(0o755)
    dest=t/'RiqatonyPad.AppDir'
    variables={
        'FINAL_APPDIR': str(dest),
        'PYI_DIST': str(t/'pyinstaller'),
        'APP_ID': 'riqatonypad',
        'APPIMAGE_PAYLOAD': str(ROOT/'packaging/appimage'),
        'HICOLOR_DIR': str(ROOT/'assets/hicolor'),
        'DOCS_DIR': str(ROOT/'docs'),
        'PROGRAM_ROOT': str(ROOT),
    }
    lines=['set -Eeuo pipefail','log() { :; }',
           'validate_desktop_entry_basic() { :; }',
           'validate_appstream_basic() { :; }']
    lines += [f'{key}={shlex.quote(value)}' for key,value in variables.items()]
    lines += ['assemble_appdir() {'+assembly+'\n}', 'assemble_appdir']
    subprocess.run(['bash','-c','\n'.join(lines)],check=True,capture_output=True,text=True)
    assert (dest/'usr/share/doc/riqatonypad/RiqatonyPad-Documentation.rtf').is_file()
    assert (dest/'usr/share/doc/riqatonypad/LICENSE').is_file()
    assert (dest/'usr/lib/riqatonypad/riqatonypad').is_file()
    assert (dest/'usr/bin/riqatonypad').is_symlink()
    assert (dest/'usr/share/applications/riqatonypad.desktop').is_file()
print('PASS: Real AppDir assembly in sandbox and documentation/plugin path consistency (1.1.2)')
