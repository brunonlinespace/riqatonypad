#!/usr/bin/env python3
"""Dependency-free structural QA for RiqatonyPad 1.0.4 Retro/Ribbon command parity."""
from pathlib import Path
import ast

from source_contract import contract_text
root = Path(__file__).resolve().parents[1]
source = contract_text(root)
ribbon_source=(root/'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
commands_source=(root/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
ribbon_tree=ast.parse(ribbon_source)
ribbon_cls=next(n for n in ribbon_tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorRibbonRetroMixin')
ribbon_methods={n.name:n for n in ribbon_cls.body if isinstance(n,ast.FunctionDef)}
tree = ast.parse(source)
commands_tree=ast.parse(commands_source)
literals = {}
for node in commands_tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        if node.targets[0].id in {'RETRO_TOOLBAR_DEFAULT', 'COMMAND_SURFACE_SPECS'}:
            literals[node.targets[0].id] = ast.literal_eval(node.value)
defaults = tuple(literals['RETRO_TOOLBAR_DEFAULT'])
specs = tuple(literals['COMMAND_SURFACE_SPECS'])
ids = [row[1] for row in specs]
allowed = set(ids)
assert ids and len(ids) == len(allowed)
assert defaults == (
    'new','open','save','undo','redo','font-face','font-size','bold','italic','underline',
    'highlight','text-color','bullet-list','align-left','align-center','indent','insert-image','insert-table','replace',
)
assert set(defaults) <= allowed
assert 'symbols' not in defaults and 'find' not in defaults and 'insert-table' in defaults and 'replace' in defaults
assert 'line-numbers' not in allowed
expected_groups=('File','Clipboard','Font','Formatting','Paragraph','Insert','Advanced','View Control','Editor Settings','Theme Settings','App Settings','Help')
seen=[]
for row in specs:
    if row[0] not in seen: seen.append(row[0])
assert tuple(seen)==expected_groups,seen
menus={row[1] for row in specs if row[3]=='menu'}
assert menus=={'editor-layout','editor-toolbar','app-theme','app-icons','app-drag-drop','dirty-duplicate','dirty-external'}
for _group,_id,_label,kind,_attr,icon in specs:
    if kind in {'action','menu'}:
        assert icon, _id
        for family in ('ribbon-icons','ribbon-icons-classic','ribbon-icons-original'):
            for variant in ('light','dark'):
                assert (root/'assets'/family/variant/f'{icon}.png').is_file(),(_id,family,variant,'png')

cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RiqatonyPad')
methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
assert not set(methods)&set(ribbon_methods)
methods.update(ribbon_methods)
command_cls=next(n for n in commands_tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorCommandsAppearanceMixin')
command_methods={n.name:n for n in command_cls.body if isinstance(n,ast.FunctionDef)}
assert not set(methods)&set(command_methods)
methods.update(command_methods)
for req in ('command_surface_catalog','build_retro_toolbar','rebuild_retro_toolbar','retro_toolbar_catalog','show_retro_toolbar_dialog','build_ribbon','set_interface_style','_refresh_retro_geometry','_attach_toolbar_context_menu','_show_toolbar_context_menu'):
    assert req in methods, req
def segment(name): return (ast.get_source_segment(ribbon_source,ribbon_methods[name]) or '') if name in ribbon_methods else ((ast.get_source_segment(commands_source,command_methods[name]) or '') if name in command_methods else (ast.get_source_segment(source,methods[name]) or ''))
assert 'return COMMAND_SURFACE_SPECS' in segment('command_surface_catalog')
assert 'return self.command_surface_catalog()' in segment('retro_toolbar_catalog')
ribbon=segment('build_ribbon')
assert 'surface_specs={spec[1]:spec for spec in self.command_surface_catalog()}' in ribbon
for helper in ('def cab(','def cfb(','def cmb(','def csel('): assert helper in ribbon
assert 'ab(g,self.' not in ribbon and 'mb(g,self.' not in ribbon

build = segment('build_retro_toolbar'); rebuild = segment('rebuild_retro_toolbar'); geometry = segment('_refresh_retro_geometry')
assert 'RibbonScrollArea(self.centralWidget())' in build and 'setWidgetResizable(False)' in build
assert 'ScrollBarAsNeeded' in build and 'ScrollBarAlwaysOff' in build
assert 'QScroller.grabGesture(' in ribbon_source and 'TouchGesture' in ribbon_source
assert 'QToolButton(self.retro_toolbar_body)' in rebuild and 'button.setDefaultAction(action)' in rebuild
assert 'if kind == "menu":' in rebuild and 'ToolButtonPopupMode.InstantPopup' in rebuild and 'button.setMenu(menu)' in rebuild
assert 'self.retro_toolbar_layout.addWidget(button)' in rebuild and 'self.retro_toolbar_layout.addWidget(widget)' in rebuild
assert 'self.retro_toolbar.addAction(action)' not in rebuild and 'widgetForAction(action)' not in rebuild
assert 'QToolBar("Retro"' not in build
assert (root/'editor_platform_startup.py').read_text(encoding='utf-8').count('qt_toolbar_ext_button') == 1 and 'findChild(QToolButton,"qt_toolbar_ext_button")' in (root/'editor_platform_startup.py').read_text(encoding='utf-8')
assert 'RIBBON_FONT_FAMILY_WIDTH = RIBBON_BUTTON_SIZE * 2' in ribbon_source
assert 'widget.setFixedSize(RIBBON_FONT_FAMILY_WIDTH,RIBBON_BUTTON_SIZE)' in geometry
assert 'widget.setFixedSize(RIBBON_BUTTON_SIZE,RIBBON_BUTTON_SIZE)' in geometry
assert 'toolbar.setFixedHeight(body_height+scrollbar_height)' in geometry
assert 'Customise Retro Bar…' in commands_source
context_menu=segment('_show_toolbar_context_menu')
assert 'self.layout_actions["ribbon"]' in context_menu and 'self.layout_actions["retro"]' in context_menu and 'self.retro_toolbar_action' in context_menu
print(f'PASS: RiqatonyPad 1.0.4 shared Ribbon/Retro registry ({len(specs)} configurable controls; {len(defaults)} defaults)')
