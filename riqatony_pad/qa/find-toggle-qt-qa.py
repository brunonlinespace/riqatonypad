#!/usr/bin/env python3
"""Fedora Qt-backed regression: actually click RiqatonyPad Ribbon and Retro Find buttons."""
from __future__ import annotations
import os, pathlib, sys, tempfile
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
STATE=tempfile.TemporaryDirectory(prefix='riqatonypad-toggle-qa-')
os.environ['XDG_CONFIG_HOME']=STATE.name
sys.argv.append('--riqatonypad-smoke-test')
PACKAGE=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(PACKAGE),str(PACKAGE.parent)]
from PyQt6.QtWidgets import QApplication,QToolButton
import app as host
host.platform_config_locations=lambda:(STATE.name,())
app=QApplication.instance() or QApplication(['riqatonypad-find-toggle-qa'])
w=host.RiqatonyPad()
w.show();app.processEvents()

def check(value,message):
    if not value:raise AssertionError(message)

def button_for(action):
    return next((b for b in w.findChildren(QToolButton) if b.defaultAction() is action and b.isVisible()),None)

def click_and_expect(button,visible,message):
    check(button is not None,'Find/Replace action button missing from current toolbar')
    button.click();app.processEvents()
    check(w.search_container.isVisible() is visible,message)

try:
    w.set_interface_style('ribbon',persist=False)
    w.ribbon_tabs.setCurrentIndex(2)  # Insert -> Advanced
    app.processEvents()
    for act,name in [(w.search_bar_action,'Find'),(w.replace_action,'Replace')]:
        button=button_for(act)
        click_and_expect(button,True,f'Ribbon {name} failed to open')
        w.text_area.setFocus();app.processEvents()
        click_and_expect(button,False,f'Ribbon {name} failed to close on repeated click')
    # Retro is configurable; include both commands in this isolated test only.
    w.retro_toolbar_items=['find','replace']
    w.rebuild_retro_toolbar()
    w.set_interface_style('retro',persist=False)
    app.processEvents()
    for act,name in [(w.search_bar_action,'Find'),(w.replace_action,'Replace')]:
        button=button_for(act)
        click_and_expect(button,True,f'Retro {name} failed to open')
        w.text_area.setFocus();app.processEvents()
        click_and_expect(button,False,f'Retro {name} failed to close on repeated click')
    # Switching active commands must keep the search surface displayed.
    w.search_bar_action.trigger();app.processEvents();check(w.search_container.isVisible(),'Find action failed to open')
    w.replace_action.trigger();app.processEvents();check(w.search_container.isVisible() and w.replace_entry.hasFocus(),'Find to Replace switch failed')
    w.hide_find_panel();app.processEvents()
    print('find-toggle-qt-qa: PASS')
finally:
    w._skip_close_save_prompt=True
    w.close()
    app.processEvents()
    STATE.cleanup()
