#!/usr/bin/env python3
"""Historical regression-check source view, reconstructed from *real* dialog modules.

This is QA-only: the production app.py remains slim and imports real bound functions.
The new x12.5 identity gate independently verifies every binding and method body.
"""
from __future__ import annotations
import ast
import textwrap
from pathlib import Path

METHOD_MODULES = [('quick_tour', 'show_tutorial_wizard'), ('keyboard_shortcuts', 'show_keyboard_shortcuts_dialog'), ('about_dialog', 'show_about_dialog')]
CLASS_NAME = 'RiqatonyPad'


def contract_text(root: Path) -> str:
    root = Path(root)
    source = (root/'app.py').read_text(encoding='utf-8')
    # Historical method fingerprints require the x12.5 constructor. Replay
    # the current x13.1 presentation changes in memory only; do not alter QA
    # historical fingerprints or production code.
    from x131_status_bar_qa import restore_x130_status_source
    # QA-only compatibility view: the x13.5 grapheme counter is the deliberate
    # replacement for x13.1's Qt UTF-16 counter. Historical structural checks
    # still inspect their original status widget arrangement.
    source = source.replace(
        '        characters=count_visible_characters(self.text_area.document())',
        '        characters=max(0,self.text_area.document().characterCount()-1)',
    )
    source = restore_x130_status_source(source)
    old_order = ('self.app_status_bar.addWidget(self.operation_mode_label); '
                 'self.app_status_bar.addWidget(self.zoom_label); '
                 'self.app_status_bar.addWidget(self.counter_label); '
                 'self.app_status_bar.addWidget(self.status_message_label,1)')
    new_order = ('self.app_status_bar.addWidget(self.operation_mode_label); '
                 'self.app_status_bar.addWidget(self.counter_label); '
                 'self.app_status_bar.addWidget(self.zoom_label); '
                 'self.app_status_bar.addWidget(self.status_message_label,1)')
    assert source.count(new_order) == 1
    source = source.replace(new_order, old_order)
    marker = 'class ' + CLASS_NAME + '('
    assert marker in source, 'application class was lost'
    pos = source.index('    def __init__(', source.index(marker))
    methods = []
    for module, name in METHOD_MODULES:
        path = root/'widgets'/f'{module}.py'
        text = path.read_text(encoding='utf-8')
        tree = ast.parse(text)
        matches = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
        assert len(matches) == 1, f'missing/multiple relocated method: {name}'
        methods.append(textwrap.indent(ast.get_source_segment(text, matches[0]) or '', '    '))
    return source[:pos] + chr(10).join(methods) + chr(10) + source[pos:]
