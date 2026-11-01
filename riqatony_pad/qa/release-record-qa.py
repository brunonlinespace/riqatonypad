#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.1.2 release-record consistency gate."""
from __future__ import annotations
import json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUTER=ROOT.parent
VERSION="2.0.0"
source=(ROOT/'app.py').read_text(encoding='utf-8')
readme=(OUTER/'README.md').read_text(encoding='utf-8')
notes=(ROOT/'docs'/'RELEASE_NOTES.md').read_text(encoding='utf-8')
changelog=(ROOT/'docs'/'CHANGELOG.md').read_text(encoding='utf-8')
manifest=json.loads((OUTER/'suite-pythoine-component.json').read_text(encoding='utf-8'))
appimage=(ROOT/'packaging'/'fedora'/'build-appimage.sh').read_text(encoding='utf-8')
appimage_test=(ROOT/'packaging'/'fedora'/'test-appimage.sh').read_text(encoding='utf-8')
windows=(ROOT/'packaging'/'windows'/'build-windows-portable.ps1').read_text(encoding='utf-8')
version_info=(ROOT/'packaging'/'windows'/'windows-version-info.txt').read_text(encoding='utf-8')
meta=ET.parse(ROOT/'packaging'/'appimage'/'io.github.brunonlinespace.riqatonypad.metainfo.xml').getroot()
assert f'APP_VERSION = "{VERSION}"' in source
assert manifest.get('version')==VERSION
assert f'APP_VERSION="{VERSION}"' in appimage
assert f'VERSION="{VERSION}"' in appimage_test
assert f'$Version = "{VERSION}"' in windows
assert 'filevers=(2, 0, 0, 0)' in version_info and 'prodvers=(2, 0, 0, 0)' in version_info
assert version_info.count("'2.0.0'")>=2
rels=meta.findall('./releases/release')
assert len(rels)==1 and rels[0].attrib.get('version')==VERSION and rels[0].attrib.get('date')=='2026-11-01'
assert f'Current release: **{VERSION}**' in readme, 'README current version'
assert f'RiqatonyPad {VERSION}' in notes, 'RELEASE_NOTES current version'
assert 'Ricopad 1.0.15' in notes and 'no Rwpyn modules' not in notes
assert 'No Rwpyn modules' in notes and 'without replacing or relocating its RTF engine or codec' in notes
assert changelog.startswith('## RiqatonyPad 2.0.0 — Stable promotion')
assert '## RiqatonyPad 2.0.0-x16.9 — Find/Replace command toggle' in changelog
assert '## RiqatonyPad 2.0.0-x16.8 — Qt QA import compatibility after app.py migration' in changelog
assert '## RiqatonyPad 2.0.0-x16.7 — Fedora AppImage builder source-layout compatibility' in changelog
assert '## RiqatonyPad 2.0.0-x16.6 — GitHub README and Halcyon dark import icon correction' in changelog
assert '## RiqatonyPad 2.0.0-x13.5 — Unicode Chars and PNG-only assets' in changelog
assert '## RiqatonyPad 2.0.0-x13.3 — Message conventions' in changelog
assert '## RiqatonyPad 2.0.0-x13.2 — Eight-message cross-family parity' in changelog
assert '## RiqatonyPad 2.0.0-x13.1 — Two-widget editor status correction' in changelog
assert '## RiqatonyPad 2.0.0-x13.0 — Editor status-bar arrangement' in changelog
assert '## RiqatonyPad 2.0.0-x12.4 — Keyboard-shortcut helper convergence' in changelog
assert '## 2.0.0-x12.3 — Widget-tree reorganisation' in changelog
assert '## 2.0.0-x12.2 — Python shebang consistency' in changelog
assert '## 2.0.0-x12.1 — Packaging-layout and provenance cleanup' in changelog
assert '## 2.0.0-x12.0 — Application module filename convergence' in changelog
assert '## 2.0.0-x11.0 — Bounded preservation and release-engineering corrections' in changelog
assert '## 2.0.0-x10.0 — Behaviour-preserving editor file-lifecycle extraction' in changelog
assert '## 1.0.14 — Quick Tour tooltip correction' in changelog
assert (ROOT/'docs/history/Ricopad-1.0.15-RELEASE_NOTES.md').is_file()
print('PASS: RiqatonyPad 2.0.0 release records and package identities are consistent')
