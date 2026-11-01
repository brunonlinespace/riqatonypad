#!/usr/bin/env python3
"""Dependency-free regression of actual Find/Replace methods, including lost focus."""
from pathlib import Path
import ast
from types import SimpleNamespace
root=Path(__file__).resolve().parents[1]
source=(root/'widgets/rwpyn/editor_search_view.py').read_text()
module=ast.parse(source)
cls=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='EditorSearchViewMixin')
methods=('toggle_find_panel','show_find_panel','hide_find_panel','toggle_search_bar','show_replace_dialog')
chosen=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in methods]
assert len(chosen)==len(methods)
fragment=ast.fix_missing_locations(ast.Module(body=[ast.ClassDef(name='SearchUnderTest',bases=[],keywords=[],body=chosen,decorator_list=[])],type_ignores=[]))
ns={'Qt':SimpleNamespace(FocusReason=SimpleNamespace(ShortcutFocusReason=1))}
exec(compile(fragment,'<real RiqatonyPad search methods>','exec'),ns)
class Input:
    def __init__(self,owner): self.owner=owner;self.focus=False
    def hasFocus(self): return self.focus
    def setFocus(self,_reason=None):
        for w in (self.owner.search_entry,self.owner.replace_entry,self.owner.text_area): w.focus=False
        self.focus=True
    def selectAll(self): pass
    def setText(self,_value): pass
class Panel:
    visible=False
    def isVisible(self):return self.visible
    def show(self):self.visible=True
    def hide(self):self.visible=False
class TextArea:
    def __init__(self,owner):self.owner=owner;self.focus=False
    def textCursor(self):return SimpleNamespace(selectedText=lambda:'')
    def setFocus(self,_reason=None):
        for w in (self.owner.search_entry,self.owner.replace_entry,self): w.focus=False
        self.focus=True
class Host(ns['SearchUnderTest']):
    def __init__(self):
        self.search_container=Panel()
        self.search_entry=Input(self)
        self.replace_entry=Input(self)
        self.text_area=TextArea(self)
        self.show_search_bar=False
        self.refresh_calls=0
        self.clear_calls=0
    def refresh_search(self):self.refresh_calls+=1
    def clear_search_results(self):self.clear_calls+=1

def check(value,msg):
    assert value,msg
h=Host()
# Find opens and a second click closes, despite focus moving to Ribbon.
check(h.toggle_find_panel(False) is True and h.search_container.isVisible(),'Find did not open')
h.text_area.setFocus()
check(h.toggle_find_panel(False) is False and not h.search_container.isVisible(),'second Find click did not close after focus left input')
check(h.text_area.hasFocus() if hasattr(h.text_area,'hasFocus') else h.text_area.focus,'editor focus was not restored')
# Replace gets exactly the same behavior.
check(h.toggle_find_panel(True) is True and h.replace_entry.hasFocus(),'Replace did not open and focus Replace')
h.text_area.setFocus()
check(h.toggle_find_panel(True) is False and not h.search_container.isVisible(),'second Replace click did not close')
# Switching modes keeps panel open, focuses requested input, then repeats close.
check(h.toggle_find_panel(False) is True,'Find did not reopen')
h.text_area.setFocus()
check(h.toggle_find_panel(True) is True and h.replace_entry.hasFocus() and h.search_container.isVisible(),'switching Find to Replace closed instead of selecting Replace')
h.text_area.setFocus()
check(h.toggle_find_panel(False) is True and h.search_entry.hasFocus(),'switching Replace to Find failed')
check(h.toggle_find_panel(False) is False and not h.search_container.isVisible(),'focused Find did not close')
# Legacy hook and show-only API must update the active-mode indicator.
h.toggle_search_bar(True);check(h.search_container.isVisible(),'legacy Show failed')
h.toggle_search_bar(False);check(not h.search_container.isVisible(),'legacy Hide failed')
h.show_replace_dialog();check(h.replace_entry.hasFocus(),'show_replace_dialog failed')
h.text_area.setFocus();check(h.toggle_find_panel(True) is False,'show-only mode was not recorded')
check(h.clear_calls>=4,'search result cleanup bypassed')
# Check the exact actionable connections and shared ribbon/retro registry, not an invented API.
actions=(root/'widgets/editor_commands_appearance.py').read_text()
assert 'self.search_bar_action.triggered.connect(lambda _checked=False:self.toggle_find_panel(False))' in actions
assert '"Find and Replace",lambda:self.toggle_find_panel(True)' in actions
ribbon=(root/'widgets/editor_ribbon_retro.py').read_text()
assert 'cab(g,"find",0,0)' in ribbon and 'cab(g,"replace",0,1)' in ribbon
assert 'button.setDefaultAction(action)' in ribbon
assert '("Advanced", "find", "Find", "action", "search_bar_action", "find")' in actions
assert '("Advanced", "replace", "Find and Replace", "action", "replace_action", "replace")' in actions
print('PASS x16.9 real Find/Replace method regression: focus loss, mode switching, toggle, actions and UI catalog')
