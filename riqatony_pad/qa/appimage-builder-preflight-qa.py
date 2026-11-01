#!/usr/bin/env python3
"""Run the actual Fedora builder's preflight/staging, then prove import closure.

No PyQt6, PyInstaller, Fedora host, downloads, or application runtime changes
are needed for this test. A full native Fedora build is still required.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "packaging/fedora/build-appimage.sh"
text = BUILDER.read_text(encoding="utf-8")
assert 'Expected the fifteen RiqatonyPad runtime Python modules' not in text
assert '${PROGRAM_ROOT}/tools' not in text
assert '"${PROGRAM_ROOT}/qa"' in text or '"$PROGRAM_ROOT/qa"' in text
assert '"$PROGRAM_ROOT/widgets"' in text
assert '--hidden-import riqatony_pad.widgets.message_conventions' in text
assert 'for iconset in new classic original aero; do' in text
assert '--paths "$SOURCE_STAGE"' in text
assert 'find "${PROGRAM_ROOT}/widgets" -type f -name' in text
assert '"$EDITOR_LIFECYCLE" "$CHARACTER_COUNT" "$MESSAGE_CONVENTIONS"' in text
subprocess.run(["bash", "-n", str(BUILDER)], check=True)

# Execute actual builder check_inputs() and stage_source() functions, not a
# copy/reimplementation of their behavior. Never run its main() or pip installs.
prelude, split = text.rsplit('\nmain "$@"', 1)
assert not split.strip(), "Unexpected builder tail after main invocation"
prelude, replacements = re.subn(
    r'^SCRIPT_DIR="\$\(cd -- "\$\(dirname -- "\$\{BASH_SOURCE\[0\]\}"\)" && pwd -P\)"$',
    f'SCRIPT_DIR={shlex.quote(str(BUILDER.parent))}',
    prelude,
    count=1,
    flags=re.M,
)
assert replacements == 1, "Could not safely bind builder source root"

with tempfile.TemporaryDirectory(prefix="riqatonypad-builder-preflight-") as td:
    staged = Path(td) / "staged"
    # Verify source requirements and generate a *real* PyInstaller staging tree.
    test_script = prelude + '\n' + '\n'.join((
        'trap - EXIT',
        f'SOURCE_STAGE={shlex.quote(str(staged))}',
        'check_inputs',
        'stage_source',
    )) + '\n'
    environment = os.environ.copy()
    environment.update({
        "RIQATONYPAD_ALLOW_ROOT_BUILD": "1",
        "RIQATONYPAD_ALLOW_UNSUPPORTED_HOST": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    proc = subprocess.run(["bash", "-c", test_script], env=environment,
                          capture_output=True, text=True, timeout=75)
    assert proc.returncode == 0, (
        "The real builder preflight/source-stage failed:\n" + proc.stdout + proc.stderr
    )

    modules = sorted(p.relative_to(ROOT) for p in ROOT.glob("*.py"))
    modules += sorted(p.relative_to(ROOT) for p in (ROOT / "widgets").rglob("*.py"))
    assert len(modules) >= 20, "Expected the extracted RTF editor module tree"
    for rel in modules:
        actual = staged / rel
        assert actual.is_file(), f"Runtime module missing from PyInstaller stage: {rel}"
        assert actual.read_bytes() == (ROOT / rel).read_bytes(), (
            f"Staged runtime file altered: {rel}"
        )

    # The application's status-message implementation has an absolute
    # riqatony_pad.widgets import, which differs from its other widgets imports.
    helper = Path('widgets/message_conventions.py')
    alternate = staged / 'riqatony_pad' / helper
    assert alternate.read_bytes() == (ROOT / helper).read_bytes()
    assert (staged / 'riqatony_pad/__init__.py').is_file()
    assert (staged / 'riqatony_pad/widgets/__init__.py').is_file()

    assert not (staged / 'qa').exists(), "Source QA was added to frozen runtime"
    assert not (staged / 'tools').exists(), "Obsolete tools staged into AppImage"

    # Resolve every local module used by actual Python import statements.
    # Not importing classes avoids Qt dependency while still finding omissions.
    sys.path.insert(0, str(staged))
    try:
        prefixes = {'widgets', 'riqatony_pad'}
        for rel in modules:
            src = (ROOT / rel).read_text(encoding='utf-8')
            tree = ast.parse(src, filename=str(rel))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    candidates = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    candidates = [node.module] if node.module else []
                else:
                    continue
                for module in candidates:
                    if module and module.split('.')[0] in prefixes:
                        assert importlib.util.find_spec(module) is not None, (
                            f"Unresolved staged import {module!r} in {rel}"
                        )
        # Negative regression: absence of the formerly omitted runtime module
        # must make the verification fail (without touching production source).
        missing = staged / 'widgets/rwpyn/character_count.py'
        assert missing.is_file()
        missing.rename(missing.with_suffix('.absent'))
        try:
            assert importlib.util.find_spec('widgets.rwpyn.character_count') is None, (
                "QA failed to detect a missing staged character_count module"
            )
        finally:
            missing.with_suffix('.absent').rename(missing)
    finally:
        sys.path.remove(str(staged))

    # A real compiler pass on every staged production module, not a substring
    # inspection of the compileall command. Redirect all cache writes to tmp.
    env = environment.copy()
    env['PYTHONPYCACHEPREFIX'] = str(Path(td) / 'pycache')
    subprocess.run([sys.executable, '-m', 'compileall', '-q', str(staged)],
                   check=True, env=env, capture_output=True, text=True)
    for theme in ('light', 'dark'):
        for family in ('ribbon-icons', 'ribbon-icons-classic',
                       'ribbon-icons-original', 'ribbon-icons-aero'):
            src = ROOT / 'assets' / family / theme
            dst = staged / family / theme
            assert sorted(p.name for p in dst.glob('*.png')) == sorted(
                p.name for p in src.glob('*.png'))
            assert len(list(dst.glob('*.png'))) == 144
    assert (staged / 'templates/default-document.rtf').is_file()
    assert (staged / 'docs/RiqatonyPad-Documentation.rtf').is_file()

print('PASS: real Fedora builder preflight + complete runtime stage/import closure, negative missing-module test, four icon families and compileall')
