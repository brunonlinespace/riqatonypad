#!/usr/bin/env python3
"""Dependency-free shared shortcut parity gate for RiqatonyPad 1.0.4."""
from __future__ import annotations
import ast
from pathlib import Path
from source_contract import contract_text
root=Path(__file__).resolve().parents[1]
source=contract_text(root)
ribbon_source=(root/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
commands_source=(root/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
ribbon_tree=ast.parse(ribbon_source)
ribbon_cls=next(n for n in ribbon_tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorRibbonRetroMixin')
ribbon_methods={n.name:n for n in ribbon_cls.body if isinstance(n,ast.FunctionDef)}

module=ast.parse(source)
command_module=ast.parse(commands_source)
methods={n.name:n for n in ast.walk(module) if isinstance(n,ast.FunctionDef)}
methods.update({n.name:n for n in ast.walk(command_module) if isinstance(n,ast.FunctionDef)})
command_names={n.name for n in ast.parse(commands_source).body if isinstance(n,ast.ClassDef) and n.name=='EditorCommandsAppearanceMixin' for n in n.body if isinstance(n,ast.FunctionDef)}
def seg(name): return (ast.get_source_segment(ribbon_source,ribbon_methods[name]) or '') if name in ribbon_methods else (ast.get_source_segment(commands_source,methods[name]) or '') if name in command_names else (ast.get_source_segment(source,methods[name]) or '')
file_menu=seg('make_file_menu'); edit=seg('make_edit_menu'); view=seg('make_view_menu'); fmt=seg('make_format_menu'); insert=seg('make_insert_menu')
expected=(
 ('New Window','Ctrl+Alt+Shift+N',file_menu),('Duplicate File','Ctrl+Shift+D',file_menu),('Properties','F4',file_menu),
 ('Export PDF','Ctrl+Alt+Shift+P',file_menu),('Duplicate Line / Selection','Ctrl+D',edit),('Delete Line','Ctrl+Shift+K',edit),
 ('Full Screen','F11',view),('Locked Mode','F12',view),('Dark Editor','Ctrl+Alt+Shift+E',view),
 ('Font…','Ctrl+Shift+F',fmt),('Increase Font Size','Ctrl+Shift+]',fmt),('Decrease Font Size','Ctrl+Shift+[',fmt),('Text Colour…','Ctrl+Shift+C',fmt),
 ('Highlight Colour','Ctrl+Shift+H',fmt),('Paragraph…','Ctrl+Shift+P',fmt),('Bullet List','Ctrl+Shift+L',fmt),
 ('Horizontal Rule','Ctrl+Alt+Shift+H',insert),
)
for label,key,segment in expected:
    assert label in segment,(label,key)
    assert f'QKeySequence("{key}")' in segment,(label,key)
for old in (
 'self.export_pdf_action = self.add_menu_action(menu, "Export PDF…", self.export_pdf, QKeySequence("Ctrl+Shift+P"))',
 'self.horizontal_rule_action=self.add_menu_action(menu,"Horizontal Rule",self.insert_horizontal_rule,QKeySequence("Ctrl+Shift+H"))',
 'self.highlight_colour_action=add("Highlight Colour…",self.choose_highlight_colour,QKeySequence("Ctrl+Alt+Shift+H"))',
 'self.paragraph_action=add("Paragraph…",self.show_paragraph_dialog,QKeySequence("Ctrl+Alt+Shift+P"))',
): assert old not in source,old
assert 'cab(g,"duplicate-line",1,0)' in seg('build_ribbon')
print('PASS: RiqatonyPad 1.0.4 shared shortcut parity and H/P exchange')
