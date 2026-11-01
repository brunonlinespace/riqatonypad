#!/usr/bin/env python3
# Ricopad
# Copyright (C) 2026 Bruno Machado
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure shortcut-search helpers ported from Rico Plus 0.0.4-r8."""

from __future__ import annotations

import re


_SHORTCUT_TOKEN_RE = re.compile(r"[a-z0-9]+|[^\w\s+]", re.IGNORECASE)
_SHORTCUT_TOKEN_ALIASES = {
    "control": "ctrl",
    "ctrl": "ctrl",
    "ctl": "ctrl",
}


def shortcut_tokens(value: str) -> tuple[str, ...]:
    """Return comparable shortcut tokens without imposing modifier order."""
    return tuple(
        _SHORTCUT_TOKEN_ALIASES.get(token, token)
        for token in _SHORTCUT_TOKEN_RE.findall(value.casefold())
    )


def shortcut_query_matches(query: str, shortcut_tokens_value: tuple[str, ...]) -> bool:
    """Match aliases, optional plus signs and reordered shortcut modifiers."""
    query_tokens = shortcut_tokens(query)
    return bool(query_tokens) and all(
        token in shortcut_tokens_value for token in query_tokens
    )

import importlib.util as _importlib_util
# Retain dependency-free shortcut search for QA without a Qt installation.
if _importlib_util.find_spec("PyQt6") is not None:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QAction, QKeySequence
    from PyQt6.QtWidgets import QAbstractItemView, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QVBoxLayout


def show_keyboard_shortcuts_dialog(self):
    """Show the live QAction shortcut inventory with Rico Plus fuzzy shortcut search."""
    if self.shortcuts_dialog is not None:
        self.shortcuts_dialog.show()
        self.shortcuts_dialog.raise_()
        self.shortcuts_dialog.activateWindow()
        return
    action_categories={}
    def collect_menu_actions(menu, category):
        for action in menu.actions():
            submenu=action.menu()
            if submenu is not None:
                collect_menu_actions(submenu,category)
            elif not action.isSeparator():
                action_categories.setdefault(action,category)
    for category,menu in (("File",self.file_menu),("Edit",self.edit_menu),("Format",self.format_menu),("Insert",self.insert_menu),("View",self.view_menu),("Settings",self.settings_menu),("Help",self.help_menu)):
        collect_menu_actions(menu,category)

    rows=[]
    seen=set()
    for action in self.findChildren(QAction):
        shortcut=action.shortcut().toString(QKeySequence.SequenceFormat.NativeText)
        label=action.text().replace("&","").replace("…","").strip()
        if shortcut and label and (label,shortcut) not in seen:
            seen.add((label,shortcut))
            rows.append((
                action_categories.get(action,"Other"),
                label,
                shortcut,
                label.casefold(),
                shortcut_tokens(shortcut),
            ))
    rows.sort(key=lambda row:row[1].casefold())
    dialog=QDialog(self)
    dialog.setWindowTitle("Keyboard Shortcuts — RiqatonyPad")
    dialog.setWindowIcon(self.windowIcon())
    dialog.setModal(False)
    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
    dialog.resize(700,560)
    layout=QVBoxLayout(dialog)
    helpers=QHBoxLayout()
    search=QLineEdit(dialog)
    search.setPlaceholderText("Search commands or shortcuts")
    search.setClearButtonEnabled(True)
    search.setAccessibleName("Search keyboard shortcuts")
    helpers.addWidget(search,1)
    category_label=QLabel("Menu:",dialog)
    helpers.addWidget(category_label)
    category_filter=QComboBox(dialog)
    category_filter.setAccessibleName("Shortcut category")
    category_filter.addItem("All","")
    for category in ("File","Edit","Format","Insert","View","Settings","Help","Other"):
        if any(row[0]==category for row in rows):
            category_filter.addItem(category,category)
    helpers.addWidget(category_filter)
    layout.addLayout(helpers)
    table=QTableWidget(len(rows),2,dialog)
    table.setHorizontalHeaderLabels(["Command","Shortcut"])
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    row_categories=[]
    for r,(category,label,key,_label_search,_shortcut_tokens) in enumerate(rows):
        row_categories.append(category)
        table.setItem(r,0,QTableWidgetItem(label)); table.setItem(r,1,QTableWidgetItem(key))
    table.resizeColumnsToContents()
    layout.addWidget(table,1)
    no_matches=QLabel("No matching shortcuts.",dialog)
    no_matches.setAlignment(Qt.AlignmentFlag.AlignCenter)
    no_matches.hide()
    layout.addWidget(no_matches)
    def filter_rows(_value=None):
        query=search.text().strip().casefold()
        selected_category=str(category_filter.currentData() or "")
        any_visible=False
        for row,(menu_name,_label,_shortcut,label_search,shortcut_search) in enumerate(rows):
            row_visible=(
                (not selected_category or selected_category==menu_name)
                and (
                    not query
                    or query in label_search
                    or shortcut_query_matches(query,shortcut_search)
                )
            )
            table.setRowHidden(row,not row_visible)
            any_visible=any_visible or row_visible
        table.setVisible(any_visible)
        no_matches.setVisible(not any_visible)
    search.textChanged.connect(filter_rows)
    category_filter.currentIndexChanged.connect(filter_rows)
    filter_rows()
    buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok,dialog)
    ok_button=buttons.button(QDialogButtonBox.StandardButton.Ok)
    if ok_button is not None: ok_button.setText("OK")
    buttons.accepted.connect(dialog.close)
    layout.addWidget(buttons)
    dialog.finished.connect(lambda _result: setattr(self, "shortcuts_dialog", None))
    self.shortcuts_dialog=dialog
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    search.setFocus()
