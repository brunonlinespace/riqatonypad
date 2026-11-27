#!/usr/bin/env python3
"""Dependency-free Phase 1C live theme-switch parity audit for RiqatonyPad 0.8.5."""
from pathlib import Path
import ast

from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
source=contract_text(ROOT)
source += '\n' + (ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
ast.parse(source)
source += '\n' + (ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
source += '\n' + (ROOT/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')

required=(
    'border: 1px solid palette(mid)',
    'self.ribbon_sections.append(frame)',
    'def refresh_interface_theme(self):',
    'sheet=frame.styleSheet()',
    'frame.setStyleSheet("")',
    'frame.setStyleSheet(sheet)',
    'style.unpolish(widget)',
    'style.polish(widget)',
    'widget.update()',
    'window.refresh_portable_icons()\n                window.refresh_interface_theme()\n                window.apply_editor_canvas_theme(update_action=True)',
)
for fragment in required:
    assert fragment in source,fragment

# The old construction-time Ribbon-border probe must be gone.
for retired in (
    'section_colour=',
    'probe=QToolButton(self.ribbon_tabs)',
    'probe.render(pm)',
):
    assert retired not in source,retired

# Re-polish must be scoped to command surfaces; editor canvas stays independently applied.
method=source[source.index('    def refresh_interface_theme(self):'):source.index('    def _schedule_interface_geometry_refresh',source.index('    def refresh_interface_theme(self):'))]
assert 'visual_editor' not in method
assert 'apply_editor_canvas_theme' not in method
assert 'ribbon_tabs' in method and 'retro_toolbar' in method and 'toolbar_stack' in method

# Phase 1C defaults/order from 0.8.3 remain intact.
for fragment in (
    'self.appimage_theme = "light"',
    'self.editor_canvas_theme = "light"',
    'for theme,label in (("light","Light"),("dark","Dark"),("system","System")):',
):
    assert fragment in source,fragment
print("PASS: RiqatonyPad 0.8.5 Phase 1C live theme-switch parity")

# 2.1.2: keep the 2.1.1 theme behavior but detach the guard cleanly before Qt/SIP teardown.
for fragment in (
    'class AppearanceThemeGuard(QObject):',
    'self._window_ref = weakref.ref(window)',
    'self._restore_timer = QTimer(self)',
    'self._restore_timer.setSingleShot(True)',
    'application.aboutToQuit.connect(self.shutdown)',
    'hints.colorSchemeChanged.connect(self._system_scheme_changed)',
    'QEvent.Type.PaletteChange',
    'QEvent.Type.ApplicationPaletteChange',
    'QEvent.Type.StyleChange',
    'self._restore_timer.start()',
    'window.apply_appimage_theme(selected)',
    'application.removeEventFilter(self)',
    'application.styleHints().colorSchemeChanged.disconnect(self._system_scheme_changed)',
    'application.aboutToQuit.disconnect(self.shutdown)',
):
    assert fragment in source, fragment
for retired in (
    'self.window = window',
    'QTimer.singleShot(0, self._restore)',
):
    assert retired not in source, retired
app_source=(ROOT/'app.py').read_text(encoding='utf-8')
assert 'self._appearance_theme_guard = AppearanceThemeGuard(self)' in app_source
print("PASS: RiqatonyPad 2.1.2 shutdown-safe MaqaronyPad-style live appearance guard")
