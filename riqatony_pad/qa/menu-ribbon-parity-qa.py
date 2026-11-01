#!/usr/bin/env python3
"""Dependency-free RiqatonyPad 1.0.4 Format/Insert/Ribbon structure parity gate."""
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
riqatonypad=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='RiqatonyPad')
methods={n.name:n for n in riqatonypad.body if isinstance(n,ast.FunctionDef)}
command_cls=next(n for n in ast.parse(commands_source).body if isinstance(n,ast.ClassDef) and n.name=='EditorCommandsAppearanceMixin')
command_methods={n.name:n for n in command_cls.body if isinstance(n,ast.FunctionDef)}
methods.update(command_methods)
def seg(name): return (ast.get_source_segment(ribbon_source,ribbon_methods[name]) or '') if name in ribbon_methods else (ast.get_source_segment(commands_source,command_methods[name]) or '') if name in command_methods else (ast.get_source_segment(source,methods[name]) or '')
fmt=seg('make_format_menu'); insert=seg('make_insert_menu'); ribbon=seg('build_ribbon')
format_order=(
 'self.font_dialog_action=add("Font…"','self.increase_font_size_action=add("Increase Font Size"','self.decrease_font_size_action=add("Decrease Font Size"','self.text_colour_action=add("Text Colour…"','self.highlight_colour_action=add("Highlight Colour…"',
 'self.bold_action=add("Bold"','self.italic_action=add("Italic"','self.underline_action=add("Underline"','self.strike_action=add("Strikethrough"','self.superscript_action=add("Superscript"','self.subscript_action=add("Subscript"',
 'self.bulleted_list_action=add("Bullet List"','self.increase_indent_action=add("Indent"','self.decrease_indent_action=add("Outdent"','self.paragraph_action=add("Paragraph…"','heading_menu=menu.addMenu("Paragraph Style")','alignment_menu=menu.addMenu("Alignment")','spacing_menu=menu.addMenu("Line Spacing")','self.clear_formatting_action=add("Clear Formatting"',)
pos=[fmt.index(x) for x in format_order]; assert pos==sorted(pos)
insert_order=('self.image_action=self.add_menu_action(menu,"Image…"','link_menu=menu.addMenu("Link")','self.table_action=self.add_menu_action(menu,"Table…"','table_edit_menu=menu.addMenu("Table Editing")','self.insert_date_time_action=self.add_menu_action(menu,"Date and Time"','self.date_action=self.add_menu_action(menu,"Date Only"','self.time_action=self.add_menu_action(menu,"Time Only"','self.horizontal_rule_action=self.add_menu_action(menu,"Horizontal Rule"','self.symbol_action=self.add_menu_action(menu,"Symbol…"')
pos=[insert.index(x) for x in insert_order]; assert pos==sorted(pos)
# Home shared surface no longer contains Advanced.
home=ribbon[ribbon.index('home=page("Home")'):ribbon.index('insert_page=page("Insert")')]
assert 'group(home,"Advanced")' not in home
# Insert keeps Images & Links / Tables / Classics and gains Plus Advanced exactly.
insert_r=ribbon[ribbon.index('insert_page=page("Insert")'):ribbon.index('view=page("Configure")')]
for required in ('group(insert_page,"Images & Links")','group(insert_page,"Tables")','group(insert_page,"Classics")','group(insert_page,"Advanced")','cab(g,"find",0,0)','cab(g,"replace",0,1)','cab(g,"duplicate-line",1,0)','cab(g,"delete-line",1,1)'):
    assert required in insert_r,required
assert insert_r.index('group(insert_page,"Images & Links")') < insert_r.index('group(insert_page,"Tables")') < insert_r.index('group(insert_page,"Classics")') < insert_r.index('group(insert_page,"Advanced")')
print('PASS: RiqatonyPad 1.0.4 Format/Insert/Home command-surface parity')
