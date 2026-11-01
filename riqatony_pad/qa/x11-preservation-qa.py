#!/usr/bin/env python3
"""RiqatonyPad x11.0 correction gate. Historical authority is never rewritten."""
from __future__ import annotations
from pathlib import Path
import hashlib, json, ast, re, os
ROOT=Path(__file__).resolve().parents[1]
OUTER=ROOT.parent
DOCS=ROOT/'docs'
HISTORICAL={'CODE_REVIEW_0.7.2.md': '5984e21b865b79291b850a0f22a588c68ac37e89b1963f0e6bf0145cc8a0049c', 'PORT_AUDIT.md': 'bb0d5f1ec7a187d495d4392fab98a82e612af955d9acea5cd1b7f84586ace338', 'LICENSING_AND_PROVENANCE.md': 'ae2f68704339a33087ea1539acd26a1f83619c5f8f5afc8237fb41afce214aac', 'SECURITY_REVIEW.md': '9a15cf2e39a6be6855f447890e3f07a9a798aaa370f93688cc467769c082c072', 'QA_TEST_PLAN.md': '66e46053f59fcec7c46d2911d6be25a677d8f2a9b250806b0995920930771f63'}
OLDER_ENTRIES={'CHANGELOG.md': '69ca47c6123264bcd6765aec102652c369472893fa29b72076db150a5d31977b', 'RELEASE_NOTES.md': '6153e6b16d4a7ddc8d9c98e0194ecc60c22e04a9b09d5d310f3e85a949fc6c57'}
EXECUTABLES=['packaging/fedora/build-appimage.sh', 'packaging/fedora/test-appimage.sh', 'portable/run-riqatonypad.sh', 'qa/appdir-layout-112-qa.py', 'qa/appmenu-icon-sync-1015-qa.py', 'qa/audit23-107-qa.py', 'qa/audit24-106-qa.py', 'qa/convergence-090-qa.py', 'qa/delete-line-qa.py', 'qa/delete-line-runtime-qa.py', 'qa/file-lifecycle-qa.py', 'qa/iconset-qa.py', 'qa/interaction-shortcuts-1010-qa.py', 'qa/libreoffice-interop-qa.py', 'qa/menu-ribbon-parity-qa.py', 'qa/missing-backing-104-qa.py', 'qa/quick-tour-1012-qa.py', 'qa/release-record-qa.py', 'qa/retro-ui-qa.py', 'qa/shell-parity-qa.py', 'qa/shortcut-parity-qa.py', 'qa/static-qa.sh', 'qa/ui-cleanup-1013-qa.py', 'qa/ui-cleanup-1014-qa.py', 'qa/ui-cleanup-103-qa.py', 'qa/ui-rework-qa.py', 'qa/word-count-qa.py']
sha=lambda b: hashlib.sha256(b).hexdigest()
for name,digest in HISTORICAL.items():
    assert sha((DOCS/name).read_bytes())==digest, f'historical Ricopad document mutated: {name}'
for name,digest in OLDER_ENTRIES.items():
    contents=(DOCS/name).read_bytes()
    if name=='CHANGELOG.md': marker=b'## 2.0.0-x10.0'
    else: marker=b'## RiqatonyPad 2.0.0-x10.0'
    assert marker in contents, name
    older=contents[contents.index(marker):]
    assert sha(older)==digest, f'pre-existing release history changed: {name}'
for name in EXECUTABLES:
    f=ROOT/name
    assert f.is_file() and f.stat().st_mode & 0o111, f'executable permission missing: {name}'
manifest=json.loads((OUTER/'suite-pythoine-component.json').read_text(encoding='utf-8'))
assert manifest['version']=='2.0.0-x13.0'
assert manifest['icon']=='riqatony_pad/assets/icons/riqatonypad.png'
assert (OUTER/manifest['icon']).is_file(), 'Suite icon path not resolvable'
source=(ROOT/'widgets/rwpyn/editor_widgets.py').read_text(encoding='utf-8')
assert 'RIQATONYPAD_INLINE_RICH_MIME = "application/x-ricopad-inline-richtext"' in source
assert 'application/x-riqatonypad-inline-richtext' not in source
assert 'source.hasFormat(RIQATONYPAD_INLINE_RICH_MIME)' in source
assert 'mime.setData(RIQATONYPAD_INLINE_RICH_MIME' in (ROOT/'widgets/rwpyn/editor_insertion.py').read_text(encoding='utf-8')
assert 'RIQATONYPAD_INLINE_RICH_MIME' in (ROOT/'qa/qt-rtf-qa.py').read_text(encoding='utf-8')
assert (DOCS/'README.md').read_text(encoding='utf-8').startswith('# RiqatonyPad 2.0.0-x13.0 documentation')
# No new preference import: the existing independent paths are deliberately maintained.
assert (ROOT/'app.py').is_file()
assert not (ROOT/'rwpyn').exists()
print('PASS: x11.0 original-history hashes, original executable modes, Suite icon, clipboard compatibility and clean cutover')
