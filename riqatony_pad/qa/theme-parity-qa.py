#!/usr/bin/env python3
"""Dependency-free Phase 1C Light-theme parity audit for RiqatonyPad 0.8.3."""
from pathlib import Path
import ast

from source_contract import contract_text
ROOT = Path(__file__).resolve().parents[1]
source = contract_text(ROOT)
source += '\n' + (ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
ast.parse(source)
source += '\n' + (ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')

required = (
    'self.appimage_theme = "light"',
    'self.editor_canvas_theme = "light"',
    'for theme,label in (("light","Light"),("dark","Dark"),("system","System")):',
    'palette.setColor(QPalette.ColorRole.Window,QColor("#D4D4D4"))',
    'palette.setColor(QPalette.ColorRole.WindowText,QColor("#2A2A2A"))',
    'palette.setColor(QPalette.ColorRole.Base,QColor("#F4F4F4"))',
    'palette.setColor(QPalette.ColorRole.AlternateBase,QColor("#E4E4E4"))',
    'palette.setColor(QPalette.ColorRole.Button,QColor("#E4E4E4"))',
    'palette.setColor(QPalette.ColorRole.Highlight,QColor("#B24A3B"))',
    'palette.setColor(QPalette.ColorRole.Link,QColor("#0068A6"))',
    'palette.setColor(QPalette.ColorRole.LinkVisited,QColor("#0068A6"))',
)
for fragment in required:
    assert fragment in source, fragment

# Saved explicit user choices must still win over the new defaults.
assert 'if saved_theme in ("system", "dark", "light"):' in source
assert 'self.appimage_theme = saved_theme' in source
assert 'if saved_canvas in ("dark", "light"):' in source
assert 'self.editor_canvas_theme = saved_canvas' in source

# This phase does not expand icon families or rewrite editor/RTF mechanics.
assert 'for icon_set,label in (("new","Riqa Icons Harmony"),("classic","Riqa Icons Humility"),("original","Riqa Icons Heritage"),("aero","Riqa Icons Halcyon")):' in source
print("PASS: RiqatonyPad 0.8.3 Phase 1C Light-theme parity")
