#!/usr/bin/env python3
# ==============================================================================
# RiqatonyPad - standalone RTF editor command and appearance methods
# Copyright (C) 2026 Bruno Machado
#
# GPLv3-or-later
#
# Version: 2.0.0-x8.0
# ==============================================================================

import base64
import html
import re
import json
import hashlib
import locale
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PyQt6.QtCore import (
    QBuffer, QByteArray, QDateTime, QEvent, QFileSystemWatcher, QIODevice, QLocale, QMimeData, QRect, QRectF,
    QRegularExpression, QSize, QSizeF, Qt, QTimer, QUrl,
)
from PyQt6.QtGui import (
    QAction, QActionGroup, QBrush, QColor, QDesktopServices, QFont, QFontDatabase, QIcon,
    QImage, QImageReader, QKeySequence, QPainter, QPalette, QPixmap, QTextBlockFormat, QTextCharFormat,
    QTextCursor, QTextDocument, QTextDocumentFragment, QTextFormat, QTextImageFormat, QTextListFormat, QTextTableFormat,
)
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QColorDialog,
    QComboBox,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFontComboBox,
    QFontDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QStyleFactory,
    QSizePolicy,
    QSpinBox,
    QScrollArea,
    QScroller,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QToolTip,
    QVBoxLayout,
    QWizard,
    QWizardPage,
    QWidget,
)

from rich_text_support import is_safe_link_target, sanitise_qt_html
from widgets.rwpyn.editor_preferences import EditorPreferencesMixin, MAX_CONFIG_FILE_SIZE, preference_bool, preference_text, resource_path
from widgets.editor_ribbon_retro import EditorRibbonRetroMixin, RibbonScrollArea, RIBBON_BUTTON_SIZE, RIBBON_ICON_SIZE, RIBBON_FONT_FAMILY_WIDTH
from widgets.rwpyn.editor_printing import EditorPrintingMixin, APP_NAME, fsync_directory, count_words
from widgets.rwpyn.editor_search_view import EditorSearchViewMixin, MAX_SEARCH_MATCHES
from widgets.rwpyn.editor_insertion import EditorInsertionMixin, read_bounded_bytes, host_process_environment, MAX_EMBEDDED_IMAGE_SIZE, MAX_IMAGE_SOURCE_SIZE, MAX_IMAGE_PIXELS
from widgets.rwpyn.editor_formatting import EditorFormattingMixin, FONT_SIZE_STEPS
from widgets.rwpyn.editor_widgets import (SafeTextDocument, RichTextEdit, MAX_PASTE_CHARACTERS,
    MAX_DOCUMENT_CHARACTERS, MAX_CLIPBOARD_HTML_CHARACTERS,
    RIQATONYPAD_INLINE_RICH_MIME, IMAGE_EXTENSIONS)
from rtf_new_document import NewDocumentDefaults, build_new_document_rtf_payload
from widgets.keyboard_shortcuts import shortcut_query_matches, shortcut_tokens
from rtf_codec import (
    _qt_brush_colour, _rtf_clear_automatic_foreground,
    decode_rtf, document_to_rtf_with_properties, populate_qtextdocument_from_rtf_model,
    RTF_SYNTHETIC_STRUCTURE_BLOCK, RTF_TABLE_AUTOFIT_PROPERTY,
    RTF_AUTOMATIC_CONTRAST_PROPERTY,
    MAX_RTF_TABLE_ROWS, MAX_RTF_TABLE_COLUMNS, MAX_RTF_TABLE_CELLS,
)


RETRO_TOOLBAR_DEFAULT = (
    "new", "open", "save", "undo", "redo",
    "font-face", "font-size", "bold", "italic", "underline",
    "highlight", "text-color", "bullet-list", "align-left", "align-center",
    "indent", "insert-image", "insert-table", "replace",
)

# group, id, label, presentation-kind, instance attribute, Rico icon name
#
# This is the single shared inventory for Ribbon and Retro. It contains normal
# QActions, menu-backed selector buttons and the four editor selectors. Ribbon
# consumes the same IDs when it builds its pages; Retro consumes the complete
# inventory when it builds the customisable one-row bar.
COMMAND_SURFACE_SPECS = (
    ("File", "new", "New", "action", "new_action", "new"),
    ("File", "open", "Open", "action", "open_action", "open"),
    ("File", "new-window", "New Window", "action", "new_window_action", "new-window"),
    ("File", "save", "Save", "action", "save_action", "save"),
    ("File", "save-as", "Save As", "action", "save_as_action", "save-as"),
    ("File", "properties", "Properties", "action", "properties_action", "properties"),
    ("File", "rename", "Rename", "action", "rename_action", "rename"),
    ("File", "external-editor", "Open in External Editor", "action", "external_editor_action", "external-editor"),
    ("File", "duplicate-file", "Duplicate File", "action", "duplicate_file_action", "duplicate-file"),
    ("File", "open-folder", "Open Containing Folder", "action", "open_folder_action", "open-folder"),
    ("File", "delete-file", "Delete File", "action", "delete_file_action", "delete-file"),
    ("File", "print", "Print", "action", "print_action", "print"),
    ("File", "export-pdf", "Export PDF", "action", "export_pdf_action", "export-pdf"),
    ("File", "page-setup", "Page Setup", "action", "page_setup_action", "page-setup"),
    ("File", "save-exit", "Save and Exit", "action", "save_exit_action", "save-exit"),
    ("File", "exit", "Exit", "action", "exit_action", "exit"),

    ("Clipboard", "undo", "Undo", "action", "undo_action", "undo"),
    ("Clipboard", "redo", "Redo", "action", "redo_action", "redo"),
    ("Clipboard", "cut", "Cut", "action", "cut_action", "cut"),
    ("Clipboard", "copy", "Copy", "action", "copy_action", "copy"),
    ("Clipboard", "paste", "Paste", "action", "paste_action", "paste"),
    ("Clipboard", "paste-plain", "Paste as Plain Text", "action", "paste_plain_action", "paste-plain"),
    ("Clipboard", "select-all", "Select All", "action", "select_all_action", "select-all"),
    ("Clipboard", "delete-text", "Delete", "action", "delete_text_action", "delete-text"),

    ("Font", "font-face", "Font Face", "font-face", None, None),
    ("Font", "font-size", "Font Size", "font-size", None, None),
    ("Font", "font-style", "Font Style", "font-style", None, None),
    ("Font", "font-size-increase", "Increase Font Size", "action", "increase_font_size_action", "font-size-increase"),
    ("Font", "font-size-decrease", "Decrease Font Size", "action", "decrease_font_size_action", "font-size-decrease"),
    ("Font", "font-dialog", "Font", "action", "font_dialog_action", "font-dialog"),

    ("Formatting", "subscript", "Subscript", "action", "subscript_action", "subscript"),
    ("Formatting", "superscript", "Superscript", "action", "superscript_action", "superscript"),
    ("Formatting", "highlight", "Highlight Colour", "action", "highlight_colour_action", "highlight"),
    ("Formatting", "text-color", "Text Colour", "action", "text_colour_action", "text-color"),
    ("Formatting", "bold", "Bold", "action", "bold_action", "bold"),
    ("Formatting", "italic", "Italic", "action", "italic_action", "italic"),
    ("Formatting", "underline", "Underline", "action", "underline_action", "underline"),
    ("Formatting", "strikethrough", "Strikethrough", "action", "strike_action", "strikethrough"),
    ("Formatting", "clear-formatting", "Clear Formatting", "action", "clear_formatting_action", "clear-formatting"),

    ("Paragraph", "indent", "Indent", "action", "increase_indent_action", "indent"),
    ("Paragraph", "outdent", "Outdent", "action", "decrease_indent_action", "outdent"),
    ("Paragraph", "bullet-list", "Bullet List", "action", "bulleted_list_action", "bullet-list"),
    ("Paragraph", "paragraph", "Paragraph", "action", "paragraph_action", "paragraph"),
    ("Paragraph", "align-left", "Align Left", "action", "alignment_left_action", "align-left"),
    ("Paragraph", "align-center", "Align Centre", "action", "alignment_center_action", "align-center"),
    ("Paragraph", "align-right", "Align Right", "action", "alignment_right_action", "align-right"),
    ("Paragraph", "justify", "Justify", "action", "alignment_justify_action", "justify"),
    ("Paragraph", "line-spacing", "Line Spacing", "line-spacing", None, None),

    ("Insert", "insert-table", "Table", "action", "table_action", "insert-table"),
    ("Insert", "delete-table", "Delete Table", "action", "table_delete_action", "delete-table"),
    ("Insert", "insert-column-left", "Insert Column Left", "action", "table_column_left_action", "insert-column-left"),
    ("Insert", "insert-column-right", "Insert Column Right", "action", "table_column_right_action", "insert-column-right"),
    ("Insert", "delete-column", "Delete Column", "action", "table_delete_column_action", "delete-column"),
    ("Insert", "insert-row-above", "Insert Row Above", "action", "table_row_above_action", "insert-row-above"),
    ("Insert", "insert-row-below", "Insert Row Below", "action", "table_row_below_action", "insert-row-below"),
    ("Insert", "delete-row", "Delete Row", "action", "table_delete_row_action", "delete-row"),
    ("Insert", "insert-link", "Insert Link", "action", "link_action", "insert-link"),
    ("Insert", "edit-link", "Edit Link", "action", "edit_link_action", "edit-link"),
    ("Insert", "remove-link", "Remove Link", "action", "remove_link_action", "remove-link"),
    ("Insert", "symbols", "Symbol", "action", "symbol_action", "symbols"),
    ("Insert", "insert-date", "Date Only", "action", "date_action", "insert-date"),
    ("Insert", "insert-image", "Image", "action", "image_action", "insert-image"),
    ("Insert", "horizontal-rule", "Horizontal Rule", "action", "horizontal_rule_action", "horizontal-rule"),
    ("Insert", "date-time", "Date and Time", "action", "insert_date_time_action", "date-time"),
    ("Insert", "insert-time", "Time Only", "action", "time_action", "insert-time"),

    ("Advanced", "find", "Find", "action", "search_bar_action", "find"),
    ("Advanced", "replace", "Find and Replace", "action", "replace_action", "replace"),
    ("Advanced", "duplicate-line", "Duplicate Line / Selection", "action", "duplicate_line_action", "duplicate-line"),
    ("Advanced", "delete-line", "Delete Line", "action", "delete_line_action", "delete-line"),

    ("View Control", "full-screen", "Full Screen", "action", "fullscreen_action", "full-screen"),
    ("View Control", "status-bar", "Show Status", "action", "status_bar_action", "status-bar"),
    ("View Control", "editor-layout", "Editor Layout", "menu", "layout_menu", "layout"),
    ("View Control", "zoom-out", "Zoom Out", "action", "zoom_out_action", "zoom-out"),
    ("View Control", "zoom-reset", "Reset Zoom", "action", "zoom_reset_action", "zoom-reset"),
    ("View Control", "zoom-in", "Zoom In", "action", "zoom_in_action", "zoom-in"),

    ("Editor Settings", "editor-toolbar", "Editor Toolbar", "menu", "interface_menu", "layout-ribbon"),
    ("Editor Settings", "tab-width", "Tab Width", "action", "tab_width_action", "tab-width"),
    ("Editor Settings", "default-font", "New Document Defaults", "action", "default_font_action", "default-font"),
    ("Editor Settings", "word-wrap", "Word Wrap", "action", "wrap_action", "word-wrap"),
    ("Editor Settings", "editor-canvas", "Dark Editor", "action", "editor_canvas_theme_action", "editor-canvas"),
    ("Editor Settings", "view-only", "Locked Mode", "action", "view_only_action", "view-only"),

    ("Theme Settings", "icons-new", "Riqa Icons Harmony", "action", "icon_new_action", "icons-new"),
    ("Theme Settings", "icons-classic", "Riqa Icons Humility", "action", "icon_classic_action", "icons-classic"),
    ("Theme Settings", "icons-original", "Riqa Icons Heritage", "action", "icon_original_action", "icons-legacy"),
    ("Theme Settings", "theme-light", "Light", "action", "theme_light_action", "theme-light"),
    ("Theme Settings", "theme-dark", "Dark", "action", "theme_dark_action", "theme-dark"),
    ("Theme Settings", "theme-system", "System", "action", "theme_system_action", "theme-system"),
    ("Theme Settings", "app-theme", "App Theme", "menu", "theme_menu", "app-theme"),
    ("Theme Settings", "app-icons", "App Icons", "menu", "app_icons_menu", "app-icons"),

    ("App Settings", "drop-active", "Opens on Active Window", "action", "drop_active_action", "drop-active"),
    ("App Settings", "drop-new-window", "Opens on New Window", "action", "drop_new_window_action", "drop-new-window"),
    ("App Settings", "app-drag-drop", "App Drag-and-Drop", "menu", "app_drag_drop_menu", "app-drag-and-drop"),
    ("App Settings", "dirty-duplicate", "Duplicate File with Unsaved Changes", "menu", "dirty_duplicate_menu", "dirty-duplicate-policy"),
    ("App Settings", "dirty-external", "Open Externally with Unsaved Changes", "menu", "dirty_external_menu", "dirty-external-policy"),

    ("Help", "github", "GitHub Repository", "action", "github_action", "github"),
    ("Help", "issue", "Raise an Issue", "action", "issue_action", "issue"),
    ("Help", "documentation", "Documentation", "action", "documentation_action", "documentation"),
    ("Help", "tutorial", "Quick Tour", "action", "tutorial_action", "tutorial"),
    ("Help", "shortcuts", "Keyboard Shortcuts", "action", "shortcuts_action", "shortcuts"),
    ("Help", "about", "About RiqatonyPad", "action", "about_action", "about"),
)
RETRO_TOOLBAR_ALLOWED = {spec[1] for spec in COMMAND_SURFACE_SPECS}



class EditorCommandsAppearanceMixin:

    def command_surface_catalog(self):
        """Return the one command inventory shared by Ribbon and Retro."""
        return COMMAND_SURFACE_SPECS

    def retro_toolbar_catalog(self):
        """Retro deliberately exposes the complete shared command inventory."""
        return self.command_surface_catalog()

    def custom_icon_variant(self):
        """Choose icons from the active AppImage theme or the host system palette."""
        if self.appimage_theme_available:
            selected=self.effective_appimage_theme()
            if selected in ("light","dark"):
                return selected
        try:
            application=QApplication.instance()
            palette=application.palette() if application is not None else self.palette()
            colour=palette.color(QPalette.ColorRole.Window)
            return "dark" if colour.lightness()<128 else "light"
        except (AttributeError,RuntimeError):
            return "light"

    def effective_appimage_icon_set(self):
        """Return the one-launch override or saved AppImage icon-family choice."""
        return self.appimage_icon_set_override or self.appimage_icon_set

    def custom_icon(self, icon_name):
        """Load one bundled RiqatonyPad icon without consulting the host theme."""
        variant = self.custom_icon_variant()
        family = {
            "classic": "ribbon-icons-classic",
            "original": "ribbon-icons-original", "aero": "ribbon-icons-aero",
        }.get(self.effective_appimage_icon_set(), "ribbon-icons")
        icon_path = resource_path(family, variant, f"{icon_name}.png")
        if os.path.isfile(icon_path):
            return QIcon(icon_path)
        # A branded application icon is safer than silently falling back to a
        # platform-dependent native glyph if a package is damaged.
        fallback = resource_path("icons", "riqatonypad.png")
        return QIcon(fallback) if os.path.isfile(fallback) else QIcon()

    def bind_custom_icon(self, target, icon_name):
        """Assign and register a bundled icon for theme-variant refreshes."""
        target.setIcon(self.custom_icon(icon_name))
        self.icon_bindings.append((target, icon_name))

    def _sync_app_drag_drop_menu_icon(self):
        """Keep the dedicated App Drag-and-Drop group icon independent of radio choice."""
        menu = getattr(self, "app_drag_drop_menu", None)
        if menu is not None:
            menu.menuAction().setIcon(self.custom_icon("app-drag-and-drop"))

    def refresh_portable_icons(self):
        """Refresh bundled icons after an AppImage theme change or host repaint."""
        for target, icon_name in tuple(self.icon_bindings):
            try:
                target.setIcon(self.custom_icon(icon_name))
            except RuntimeError:
                continue
        for target, icon_name in tuple(getattr(self, "retro_icon_bindings", ())):
            try:
                target.setIcon(self.custom_icon(icon_name))
            except RuntimeError:
                continue
        self._sync_app_drag_drop_menu_icon()

    def add_menu_action(
        self, menu, label, callback, shortcut=None, *, checkable=False,
    ):
        """Create a shared command action in a hidden menu container.

        The Ribbon and Retro presentations share these actions. Retro exposes
        the native-capable menu bar; Ribbon exposes the same commands as controls.
        """
        action = QAction(label, self)
        action.setCheckable(bool(checkable))
        action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(shortcut)
        menu.addAction(action)
        # Register the shared action on the window as well so its shortcut
        # remains active even though the legacy menu bar is hidden.
        self.addAction(action)
        return action

    def make_file_menu(self):
        menu = QMenu("&File", self); self.file_menu = menu; self.app_menu_bar.addMenu(menu)
        self.new_action = self.add_menu_action(menu, "New", self.new_file, QKeySequence.StandardKey.New)
        self.new_window_action = self.add_menu_action(menu, "New Window", self.new_window, QKeySequence("Ctrl+Alt+Shift+N"))
        self.open_action = self.add_menu_action(menu, "Open…", self.open_file, QKeySequence.StandardKey.Open)
        menu.addSeparator()
        self.save_action = self.add_menu_action(menu, "Save", self.save_file, QKeySequence.StandardKey.Save)
        self.save_as_action = self.add_menu_action(menu, "Save As…", self.save_as_file, QKeySequence.StandardKey.SaveAs)
        self.more_actions_menu = menu.addMenu("More Actions")
        self.duplicate_file_action = self.add_menu_action(self.more_actions_menu, "Duplicate File…", self.duplicate_current_file, QKeySequence("Ctrl+Shift+D"))
        self.rename_action = self.add_menu_action(self.more_actions_menu, "Rename File…", self.rename_current_file, QKeySequence("F2"))
        self.delete_file_action = self.add_menu_action(self.more_actions_menu, "Delete File", self.delete_current_file)
        self.more_actions_menu.addSeparator()
        self.external_editor_action = self.add_menu_action(self.more_actions_menu, "Open in External Editor", self.open_external_editor, QKeySequence("Ctrl+Shift+E"))
        self.open_folder_action = self.add_menu_action(self.more_actions_menu, "Open Containing Folder", self.open_containing_folder, QKeySequence("Ctrl+Shift+O"))
        self.more_actions_menu.addSeparator()
        self.properties_action = self.add_menu_action(self.more_actions_menu, "Properties", self.show_properties_dialog, QKeySequence("F4"))
        self.file_dependent_actions.extend([self.external_editor_action,self.rename_action,self.delete_file_action,self.duplicate_file_action,self.open_folder_action])
        menu.addSeparator()
        self.print_action = self.add_menu_action(menu, "Print…", self.print_document, QKeySequence.StandardKey.Print)
        self.export_pdf_action = self.add_menu_action(menu, "Export PDF…", self.export_pdf, QKeySequence("Ctrl+Alt+Shift+P"))
        self.page_setup_action = self.add_menu_action(menu, "Page Setup…", self.show_page_setup_dialog)
        menu.addSeparator()
        self.exit_action = self.add_menu_action(menu, "Exit", self.close, QKeySequence.StandardKey.Quit)
        self.save_exit_action = self.add_menu_action(menu, "Save and Exit", self.save_and_exit, QKeySequence("Ctrl+Shift+Q"))

    def make_edit_menu(self):
        menu=QMenu("&Edit",self); self.edit_menu=menu; self.app_menu_bar.addMenu(menu)
        self.undo_action=self.add_menu_action(menu,"Undo",self.text_area_undo,QKeySequence.StandardKey.Undo)
        self.redo_action=self.add_menu_action(menu,"Redo",self.text_area_redo,QKeySequence("Ctrl+Y")); menu.addSeparator()
        self.cut_action=self.add_menu_action(menu,"Cut",self.cut_selection,QKeySequence.StandardKey.Cut)
        self.copy_action=self.add_menu_action(menu,"Copy",self.copy_selection,QKeySequence.StandardKey.Copy)
        self.paste_action=self.add_menu_action(menu,"Paste",lambda:self.text_area.paste(),QKeySequence.StandardKey.Paste)
        self.paste_plain_action=self.add_menu_action(menu,"Paste as Plain Text",self.paste_plain_text,QKeySequence("Ctrl+Shift+V")); menu.addSeparator()
        self.delete_text_action=self.add_menu_action(menu,"Delete",self.delete_selection,QKeySequence.StandardKey.Delete); menu.addSeparator()
        self.duplicate_line_action=self.add_menu_action(menu,"Duplicate Line / Selection",self.duplicate_current_line,QKeySequence("Ctrl+D"))
        self.delete_line_action=self.add_menu_action(menu,"Delete Line",self.delete_current_line,QKeySequence("Ctrl+Shift+K")); menu.addSeparator()
        self.select_all_action=self.add_menu_action(menu,"Select All",lambda:self.text_area.selectAll(),QKeySequence.StandardKey.SelectAll); menu.addSeparator()
        self.search_bar_action=QAction("Find",self); self.search_bar_action.setShortcut(QKeySequence.StandardKey.Find); self.search_bar_action.setToolTip("Open or focus Find"); self.search_bar_action.setStatusTip("Open or focus Find"); self.search_bar_action.triggered.connect(lambda _checked=False:self.toggle_find_panel(False)); self.addAction(self.search_bar_action); menu.addAction(self.search_bar_action)
        self.replace_action=self.add_menu_action(menu,"Find and Replace",lambda:self.toggle_find_panel(True),QKeySequence("Ctrl+H"))
        self.editing_actions.extend([self.undo_action,self.redo_action,self.cut_action,self.paste_action,self.paste_plain_action,self.delete_text_action,self.duplicate_line_action,self.delete_line_action,self.replace_action])

    def make_view_menu(self):
        menu=QMenu("&View",self); self.view_menu=menu; self.app_menu_bar.addMenu(menu)
        self.fullscreen_action=self.add_menu_action(menu,"Full Screen",self.toggle_fullscreen,QKeySequence("F11"),checkable=True)
        self.status_bar_action=self.add_menu_action(menu,"Show Status",self.toggle_status_bar,QKeySequence("Ctrl+Alt+Shift+S"),checkable=True)
        menu.addSeparator()
        self.wrap_action=self.add_menu_action(menu,"Word Wrap",self.toggle_word_wrap,QKeySequence("Ctrl+Alt+Shift+W"),checkable=True)
        self.editor_canvas_theme_action=self.add_menu_action(menu,"Dark Editor",self.toggle_editor_canvas_light,QKeySequence("Ctrl+Alt+Shift+E"),checkable=True)
        menu.addSeparator()
        self.view_only_action=self.add_menu_action(menu,"Locked Mode",self.toggle_view_only,QKeySequence("F12"),checkable=True)
        self.layout_menu=menu.addMenu("Editor Layout"); self.workspace_layout_group=QActionGroup(self); self.workspace_layout_group.setExclusive(True); self.workspace_layout_actions={}
        for mode,label,shortcut in ((3,"Toolbar Top / Find Bottom","Ctrl+Alt+Shift+1"),(1,"Toolbar Top / Find Top","Ctrl+Alt+Shift+2"),(4,"Toolbar Bottom / Find Top","Ctrl+Alt+Shift+3"),(2,"Toolbar Bottom / Find Bottom","Ctrl+Alt+Shift+4")):
            action=QAction(label,self,checkable=True); action.setShortcut(QKeySequence(shortcut)); action.triggered.connect(lambda _checked=False,selected=mode:self.set_workspace_layout(selected)); self.workspace_layout_group.addAction(action); self.layout_menu.addAction(action); self.addAction(action); self.workspace_layout_actions[mode]=action
        self.interface_menu=menu.addMenu("Editor Toolbar")
        self.layout_group=QActionGroup(self); self.layout_group.setExclusive(True); self.layout_actions={}
        for mode,label in (("ribbon","Ribbon (default)"),("retro","Retro")):
            action=QAction(label,self,checkable=True); action.triggered.connect(lambda _checked=False,selected=mode:self.set_interface_style(selected)); self.layout_group.addAction(action); self.interface_menu.addAction(action); self.addAction(action); self.layout_actions[mode]=action
            self.bind_custom_icon(action,"toolbar-tabbed" if mode=="ribbon" else "toolbar-classic")
        self.toggle_interface_style_action=QAction("Toggle Ribbon/Retro",self); self.toggle_interface_style_action.setShortcut(QKeySequence("Ctrl+Alt+Shift+T")); self.toggle_interface_style_action.triggered.connect(lambda _checked=False:self.set_interface_style("retro" if self.interface_style=="ribbon" else "ribbon")); self.addAction(self.toggle_interface_style_action)
        self.retro_toolbar_separator=self.interface_menu.addSeparator()
        self.retro_toolbar_action=self.add_menu_action(self.interface_menu,"Customise Retro Bar…",self.show_retro_toolbar_dialog)
        menu.addSeparator()
        zoom_menu=menu.addMenu("Editor Zoom")
        self.zoom_in_action=self.add_menu_action(zoom_menu,"Zoom In",self.zoom_in,QKeySequence.StandardKey.ZoomIn)
        self.zoom_out_action=self.add_menu_action(zoom_menu,"Zoom Out",self.zoom_out,QKeySequence.StandardKey.ZoomOut)
        zoom_menu.addSeparator()
        self.zoom_reset_action=self.add_menu_action(zoom_menu,"Reset Zoom",self.zoom_reset,QKeySequence("Ctrl+0"))
        self.editor_misc_menu=menu.addMenu("Editor Miscellaneous")
        self.tab_width_action=self.add_menu_action(self.editor_misc_menu,"Tab Width…",self.open_tab_width_dialog)
        self.default_font_action=self.add_menu_action(self.editor_misc_menu,"New Document Defaults…",self.show_new_document_defaults_dialog)
        self.appimage_dark_mode_action=None

    def make_settings_menu(self):
        menu=QMenu("&Settings",self); self.settings_menu=menu; self.app_menu_bar.addMenu(menu)
        self.theme_menu=menu.addMenu("App Theme")
        self.appimage_theme_group=QActionGroup(self); self.appimage_theme_group.setExclusive(True); self.appimage_theme_actions={}
        for theme,label in (("light","Light"),("dark","Dark"),("system","System")):
            action=QAction(label,self,checkable=True); action.setEnabled(bool(self.appimage_theme_available)); action.setProperty("riqatonypad_toolbar_tooltip",f"Theme — {label}")
            action.triggered.connect(lambda _checked=False,selected=theme:self.set_appimage_theme(selected))
            self.appimage_theme_group.addAction(action); self.theme_menu.addAction(action); self.addAction(action); self.appimage_theme_actions[theme]=action
        self.theme_light_action=self.appimage_theme_actions["light"]; self.theme_dark_action=self.appimage_theme_actions["dark"]; self.theme_system_action=self.appimage_theme_actions["system"]
        self.app_icons_menu=menu.addMenu("App Icons")
        self.appimage_icon_group=QActionGroup(self); self.appimage_icon_group.setExclusive(True); self.appimage_icon_actions={}
        for icon_set,label in (("new","Riqa Icons Harmony"),("classic","Riqa Icons Humility"),("original","Riqa Icons Heritage"),("aero","Riqa Icons Halcyon")):
            action=QAction(label,self,checkable=True)
            action.triggered.connect(lambda _checked=False,selected=icon_set:self.set_appimage_icon_set(selected))
            self.appimage_icon_group.addAction(action); self.app_icons_menu.addAction(action); self.addAction(action); self.appimage_icon_actions[icon_set]=action
        self.icon_new_action=self.appimage_icon_actions["new"]; self.icon_classic_action=self.appimage_icon_actions["classic"]; self.icon_original_action=self.appimage_icon_actions["original"]
        self.app_drag_drop_menu=menu.addMenu("App Drag-and-Drop"); self.behaviour_group=QActionGroup(self); self.behaviour_group.setExclusive(True); self.drop_behaviour_actions={}
        for mode,label in (("active_window","Opens on Active Window"),("new_window","Opens on New Window")):
            action=QAction(label,self,checkable=True); action.setProperty("riqatonypad_toolbar_tooltip",f"Drag-and-Drop — {label}"); action.triggered.connect(lambda _checked=False,selected=mode:self.set_drop_open_mode(selected)); self.behaviour_group.addAction(action); self.app_drag_drop_menu.addAction(action); self.addAction(action); self.drop_behaviour_actions[mode]=action
        self.drop_active_action=self.drop_behaviour_actions["active_window"]; self.drop_new_window_action=self.drop_behaviour_actions["new_window"]
        menu.addSeparator()
        self.dirty_duplicate_menu=menu.addMenu("Duplicate File with Unsaved Changes")
        self.dirty_duplicate_group=QActionGroup(self); self.dirty_duplicate_group.setExclusive(True); self.dirty_duplicate_actions={}
        for choice,label in (("ask","Ask Every Time"),("current","Duplicate Current Document"),("saved","Duplicate Last Saved Version")):
            action=QAction(label,self,checkable=True); action.triggered.connect(lambda _checked=False,selected=choice:self.set_dirty_duplicate_action(selected)); self.dirty_duplicate_group.addAction(action); self.dirty_duplicate_menu.addAction(action); self.addAction(action); self.dirty_duplicate_actions[choice]=action
        self.dirty_external_menu=menu.addMenu("Open Externally with Unsaved Changes")
        self.dirty_external_group=QActionGroup(self); self.dirty_external_group.setExclusive(True); self.dirty_external_actions={}
        for choice,label in (("ask","Ask Every Time"),("save","Save Changes and Open"),("saved","Open Last Saved Version")):
            action=QAction(label,self,checkable=True); action.triggered.connect(lambda _checked=False,selected=choice:self.set_dirty_external_action(selected)); self.dirty_external_group.addAction(action); self.dirty_external_menu.addAction(action); self.addAction(action); self.dirty_external_actions[choice]=action

    def make_insert_menu(self):
        menu=QMenu("&Insert",self); self.insert_menu=menu; self.app_menu_bar.addMenu(menu)
        self.image_action=self.add_menu_action(menu,"Image…",self.insert_image,QKeySequence("Ctrl+Shift+I"))
        link_menu=menu.addMenu("Link"); self.bind_custom_icon(link_menu.menuAction(),"link-group")
        self.link_action=self.add_menu_action(link_menu,"Insert Link…",self.insert_link,QKeySequence("Ctrl+K"))
        self.edit_link_action=self.add_menu_action(link_menu,"Edit Link…",self.edit_link)
        link_menu.addSeparator()
        self.remove_link_action=self.add_menu_action(link_menu,"Remove Link",self.remove_link)
        menu.addSeparator()
        self.table_action=self.add_menu_action(menu,"Table…",self.insert_table,QKeySequence("Ctrl+Shift+T"))
        table_edit_menu=menu.addMenu("Table Editing")
        self.table_row_above_action=self.add_menu_action(table_edit_menu,"Insert Row Above",self.insert_table_row_above)
        self.table_row_below_action=self.add_menu_action(table_edit_menu,"Insert Row Below",self.insert_table_row_below)
        self.table_delete_row_action=self.add_menu_action(table_edit_menu,"Delete Row",self.delete_table_row); table_edit_menu.addSeparator()
        self.table_column_left_action=self.add_menu_action(table_edit_menu,"Insert Column Left",self.insert_table_column_left)
        self.table_column_right_action=self.add_menu_action(table_edit_menu,"Insert Column Right",self.insert_table_column_right)
        self.table_delete_column_action=self.add_menu_action(table_edit_menu,"Delete Column",self.delete_table_column); table_edit_menu.addSeparator()
        self.table_delete_action=self.add_menu_action(table_edit_menu,"Delete Table",self.delete_table)
        menu.addSeparator()
        self.insert_date_time_action=self.add_menu_action(menu,"Date and Time",self.insert_time_date,QKeySequence("F5"))
        self.date_action=self.add_menu_action(menu,"Date Only",self.insert_date,QKeySequence("Ctrl+;"))
        self.time_action=self.add_menu_action(menu,"Time Only",self.insert_time,QKeySequence("Ctrl+:"))
        menu.addSeparator()
        self.horizontal_rule_action=self.add_menu_action(menu,"Horizontal Rule",self.insert_horizontal_rule,QKeySequence("Ctrl+Alt+Shift+H"))
        self.symbol_action=self.add_menu_action(menu,"Symbol…",self.show_symbols_popup,QKeySequence("Shift+F5"))
        self.table_edit_actions=[self.table_row_above_action,self.table_row_below_action,self.table_delete_row_action,self.table_column_left_action,self.table_column_right_action,self.table_delete_column_action,self.table_delete_action]
        self.visual_insert_actions.extend([self.insert_date_time_action,self.date_action,self.time_action,self.image_action,self.link_action,self.edit_link_action,self.remove_link_action,self.horizontal_rule_action,self.table_action,*self.table_edit_actions])

    def make_format_menu(self):
        menu=QMenu("F&ormat",self); self.format_menu=menu; self.app_menu_bar.addMenu(menu)
        def add(label,callback,shortcut=None):
            action=self.add_menu_action(menu,label,callback,shortcut); self.format_actions.append(action); return action
        self.font_dialog_action=add("Font…",self.choose_selection_font,QKeySequence("Ctrl+Shift+F"))
        self.increase_font_size_action=add("Increase Font Size",self.increase_font_size,QKeySequence("Ctrl+Shift+]"))
        self.decrease_font_size_action=add("Decrease Font Size",self.decrease_font_size,QKeySequence("Ctrl+Shift+["))
        self.text_colour_action=add("Text Colour…",self.choose_text_colour,QKeySequence("Ctrl+Shift+C"))
        self.highlight_colour_action=add("Highlight Colour…",self.choose_highlight_colour,QKeySequence("Ctrl+Shift+H"))
        menu.addSeparator()
        self.bold_action=add("Bold",self.toggle_bold,QKeySequence.StandardKey.Bold); self.bold_action.setCheckable(True)
        self.italic_action=add("Italic",self.toggle_italic,QKeySequence.StandardKey.Italic); self.italic_action.setCheckable(True)
        self.underline_action=add("Underline",self.toggle_underline,QKeySequence.StandardKey.Underline); self.underline_action.setCheckable(True)
        self.strike_action=add("Strikethrough",self.toggle_strikethrough,QKeySequence("Ctrl+Shift+X")); self.strike_action.setCheckable(True)
        self.superscript_action=add("Superscript",self.toggle_superscript,QKeySequence("Ctrl+.")); self.superscript_action.setCheckable(True)
        self.subscript_action=add("Subscript",self.toggle_subscript,QKeySequence("Ctrl+,")); self.subscript_action.setCheckable(True)
        menu.addSeparator()
        self.bulleted_list_action=add("Bullet List",self.toggle_bullet_list,QKeySequence("Ctrl+Shift+L")); self.bulleted_list_action.setCheckable(True)
        self.increase_indent_action=add("Indent",lambda:self.change_indent(1),QKeySequence("Ctrl+]"))
        self.decrease_indent_action=add("Outdent",lambda:self.change_indent(-1),QKeySequence("Ctrl+[")); menu.addSeparator()
        self.paragraph_action=add("Paragraph…",self.show_paragraph_dialog,QKeySequence("Ctrl+Shift+P"))
        heading_menu=menu.addMenu("Paragraph Style"); self.bind_custom_icon(heading_menu.menuAction(),"heading-group"); self.heading_actions={}
        for label,level,shortcut in (("Normal Paragraph",0,"Ctrl+Shift+0"),("Heading 1",1,"Ctrl+Shift+1"),("Heading 2",2,"Ctrl+Shift+2"),("Heading 3",3,"Ctrl+Shift+3"),("Heading 4",4,"Ctrl+Shift+4"),("Heading 5",5,"Ctrl+Shift+5"),("Heading 6",6,"Ctrl+Shift+6")):
            action=QAction(label,self,checkable=True); action.setShortcut(QKeySequence(shortcut)); action.triggered.connect(lambda _checked=False,selected=level:self.apply_heading(selected)); heading_menu.addAction(action); self.addAction(action); self.bind_custom_icon(action,f"heading-{level}"); self.heading_actions[level]=action; self.format_actions.append(action)
        alignment_menu=menu.addMenu("Alignment"); self.alignment_actions={}
        for label,alignment,shortcut in (("Left",Qt.AlignmentFlag.AlignLeft,"Ctrl+L"),("Centre",Qt.AlignmentFlag.AlignHCenter,"Ctrl+E"),("Right",Qt.AlignmentFlag.AlignRight,"Ctrl+R"),("Justify",Qt.AlignmentFlag.AlignJustify,"Ctrl+J")):
            action=QAction(label,self,checkable=True); action.setShortcut(QKeySequence(shortcut)); action.triggered.connect(lambda _checked=False,selected=alignment:self.set_alignment(selected)); alignment_menu.addAction(action); self.addAction(action); self.alignment_actions[alignment]=action; self.format_actions.append(action)
        self.alignment_left_action=self.alignment_actions[Qt.AlignmentFlag.AlignLeft]; self.alignment_center_action=self.alignment_actions[Qt.AlignmentFlag.AlignHCenter]; self.alignment_right_action=self.alignment_actions[Qt.AlignmentFlag.AlignRight]; self.alignment_justify_action=self.alignment_actions[Qt.AlignmentFlag.AlignJustify]
        spacing_menu=menu.addMenu("Line Spacing"); self.line_spacing_actions={}
        for label,percent,shortcut in (("1.0",100,"Ctrl+1"),("1.15",115,"Ctrl+2"),("1.5",150,"Ctrl+3"),("2.0",200,"Ctrl+4")):
            action=QAction(label,self,checkable=True); action.setShortcut(QKeySequence(shortcut)); action.triggered.connect(lambda _checked=False,selected=percent:self.set_line_spacing(selected)); spacing_menu.addAction(action); self.addAction(action); self.line_spacing_actions[percent]=action; self.format_actions.append(action)
        menu.addSeparator()
        self.clear_formatting_action=add("Clear Formatting",self.clear_formatting,QKeySequence("Ctrl+Space"))

    def make_help_menu(self):
        menu = QMenu("&Help", self)
        self.help_menu = menu
        self.app_menu_bar.addMenu(menu)
        self.documentation_action = self.add_menu_action(
            menu, "Documentation", self.open_documentation, QKeySequence("F1")
        )
        menu.addSeparator()
        self.tutorial_action = self.add_menu_action(
            menu, "Quick Tour…", self.show_tutorial_wizard,
            QKeySequence("Shift+F1")
        )
        self.tutorial_action.setToolTip("Quick Tour… — Shift+F1")
        self.tutorial_action.setProperty("riqatonypad_toolbar_tooltip", "Quick Tour…")
        self.shortcuts_action = self.add_menu_action(
            menu, "Keyboard Shortcuts", self.show_keyboard_shortcuts_dialog,
            QKeySequence("Ctrl+Shift+/")
        )
        menu.addSeparator()
        self.github_action = self.add_menu_action(
            menu, "GitHub Repository", self.open_github_repository
        )
        self.issue_action = self.add_menu_action(
            menu, "Raise an Issue", self.report_an_issue
        )
        menu.addSeparator()
        self.about_action = self.add_menu_action(
            menu, "About RiqatonyPad", self.show_about_dialog
        )
        self.about_action.setMenuRole(QAction.MenuRole.AboutRole)

    def bind_shortcuts(self):
        """Own transient Find/Replace keys at the standalone window boundary."""
        self.find_next_shortcut_action=QAction("Find Next",self)
        self.find_next_shortcut_action.setShortcut(QKeySequence("F3"))
        self.find_next_shortcut_action.triggered.connect(self.find_next)
        self.addAction(self.find_next_shortcut_action)
        self.find_previous_shortcut_action=QAction("Find Previous",self)
        self.find_previous_shortcut_action.setShortcut(QKeySequence("Shift+F3"))
        self.find_previous_shortcut_action.triggered.connect(self.find_previous)
        self.addAction(self.find_previous_shortcut_action)
        self.close_find_shortcut_action=QAction("Close Find/Replace",self)
        self.close_find_shortcut_action.setShortcut(QKeySequence("Esc"))
        self.close_find_shortcut_action.triggered.connect(lambda:self.hide_find_panel() if self.search_container.isVisible() else None)
        self.addAction(self.close_find_shortcut_action)

    def infer_editor_canvas_theme(self):
        """Infer the existing editor appearance without changing it.

        First launch therefore follows the active host or bundled AppImage
        theme. After the user presses the toggle, the explicit light/dark
        choice is persisted independently of the application chrome.
        """
        if self.appimage_theme_available:
            selected = self.effective_appimage_theme()
            if selected in ("light", "dark"):
                return selected
        colour = self.visual_editor.palette().color(QPalette.ColorRole.Base)
        return "light" if colour.lightness() >= 128 else "dark"

    def update_editor_canvas_theme_action(self):
        action = getattr(self, "editor_canvas_theme_action", None)
        if action is None:
            return
        is_dark = self.editor_canvas_theme == "dark"
        current = "Dark" if is_dark else "Light"
        target = "light" if is_dark else "dark"
        shortcut=action.shortcut().toString(QKeySequence.SequenceFormat.NativeText)
        tooltip = (
            f"Dark Editor ({shortcut}) — editor canvas: {current}. Click for {target}; "
            "the ribbon and the rest of the interface will not change."
        ) if shortcut else (
            f"Dark Editor — editor canvas: {current}. Click for {target}; "
            "the ribbon and the rest of the interface will not change."
        )
        action.blockSignals(True)
        action.setChecked(is_dark)
        action.setToolTip(tooltip)
        action.setStatusTip(f"Editor canvas appearance: {current}")
        action.blockSignals(False)
        for button in getattr(self, "ribbon_buttons", ()):
            try:
                if button.defaultAction() is action:
                    button.setToolTip(tooltip)
                    button.setStatusTip(action.statusTip())
                    button.setAccessibleName(f"Editor canvas appearance: {current}")
            except RuntimeError:
                continue

    def apply_editor_canvas_theme(self, update_action=True):
        """Apply a display-only light/dark canvas override without rewriting RTF formatting."""
        if not hasattr(self,"visual_editor"): return
        if self.editor_canvas_theme not in ("light","dark"): self.editor_canvas_theme=self.infer_editor_canvas_theme()
        editor=self.visual_editor
        # Exact Markopad canvas-palette model in every runtime, with only the
        # product accent changed from teal to RiqatonyPad brick. Do not QSS-paint
        # the editor in Portable/source or AppImage.
        palette=QPalette(editor.palette())
        if self.editor_canvas_theme == "light":
            palette.setColor(QPalette.ColorRole.Base,QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Text,QColor("#202124"))
            palette.setColor(QPalette.ColorRole.Highlight,QColor("#B24A3B"))
            palette.setColor(QPalette.ColorRole.HighlightedText,QColor("#FFFFFF"))
        else:
            palette.setColor(QPalette.ColorRole.Base,QColor("#151719"))
            palette.setColor(QPalette.ColorRole.Text,QColor("#F1F3F4"))
            palette.setColor(QPalette.ColorRole.Highlight,QColor("#B24A3B"))
            palette.setColor(QPalette.ColorRole.HighlightedText,QColor("#FFFFFF"))
        editor.setPalette(palette)
        editor.viewport().setPalette(palette)
        editor.setStyleSheet("")
        editor.viewport().setAutoFillBackground(True)
        editor.setContentsMargins(0,0,0,0)
        editor.setViewportMargins(0,0,0,0)
        editor.document().setDocumentMargin(4.0)
        editor.viewport().update()
        if update_action: self.update_editor_canvas_theme_action()

    def toggle_editor_canvas_light(self, checked):
        # The View action is named "Dark Editor": checked means dark.
        self.editor_canvas_theme = "dark" if bool(checked) else "light"
        self.apply_editor_canvas_theme(update_action=True)
        self.save_preferences()
        self._show_status_message(
            "Editor canvas switched to a dark background."
            if self.editor_canvas_theme == "dark"
            else "Editor canvas switched to a light background.",
            3000,
        )

    def effective_appimage_theme(self):
        """Return the explicit launch override or saved AppImage System/Dark/Light choice."""
        return self.appimage_theme_override or self.appimage_theme

    def _portable_markopad_palette(self, theme):
        """Return Markopad's exact Portable Dark/Light palette with Rico brick accent."""
        palette=QPalette()
        if theme == "dark":
            palette.setColor(QPalette.ColorRole.Window,QColor("#202326"))
            palette.setColor(QPalette.ColorRole.WindowText,QColor("#F1F3F4"))
            palette.setColor(QPalette.ColorRole.Base,QColor("#151719"))
            palette.setColor(QPalette.ColorRole.AlternateBase,QColor("#202326"))
            palette.setColor(QPalette.ColorRole.ToolTipBase,QColor("#F1F3F4"))
            palette.setColor(QPalette.ColorRole.ToolTipText,QColor("#101214"))
            palette.setColor(QPalette.ColorRole.Text,QColor("#F1F3F4"))
            palette.setColor(QPalette.ColorRole.Button,QColor("#292D31"))
            palette.setColor(QPalette.ColorRole.ButtonText,QColor("#F1F3F4"))
            palette.setColor(QPalette.ColorRole.Highlight,QColor("#B24A3B"))
            palette.setColor(QPalette.ColorRole.HighlightedText,QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.PlaceholderText,QColor("#8E969E"))
        else:
            application=QApplication.instance()
            palette=QPalette(application.style().standardPalette()) if application is not None else QPalette()
            palette.setColor(QPalette.ColorRole.Window,QColor("#D4D4D4"))
            palette.setColor(QPalette.ColorRole.WindowText,QColor("#2A2A2A"))
            palette.setColor(QPalette.ColorRole.Base,QColor("#F4F4F4"))
            palette.setColor(QPalette.ColorRole.AlternateBase,QColor("#E4E4E4"))
            palette.setColor(QPalette.ColorRole.ToolTipBase,QColor("#F4F4F4"))
            palette.setColor(QPalette.ColorRole.ToolTipText,QColor("#2A2A2A"))
            palette.setColor(QPalette.ColorRole.Text,QColor("#2A2A2A"))
            palette.setColor(QPalette.ColorRole.Button,QColor("#E4E4E4"))
            palette.setColor(QPalette.ColorRole.ButtonText,QColor("#2A2A2A"))
            palette.setColor(QPalette.ColorRole.Light,QColor("#F4F4F4"))
            palette.setColor(QPalette.ColorRole.Midlight,QColor("#D0D0D0"))
            palette.setColor(QPalette.ColorRole.Mid,QColor("#B2B2B2"))
            palette.setColor(QPalette.ColorRole.Dark,QColor("#767676"))
            palette.setColor(QPalette.ColorRole.Shadow,QColor("#545454"))
            palette.setColor(QPalette.ColorRole.Highlight,QColor("#B24A3B"))
            palette.setColor(QPalette.ColorRole.HighlightedText,QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.PlaceholderText,QColor("#767676"))
            palette.setColor(QPalette.ColorRole.Link,QColor("#0068A6"))
            palette.setColor(QPalette.ColorRole.LinkVisited,QColor("#0068A6"))
        return palette

    def _appimage_palette(self, theme):
        """Return a complete AppImage palette independent of the host theme."""
        application = QApplication.instance()
        base_palette = QPalette(application.palette()) if application is not None else QPalette()
        if theme == "dark":
            colours = {
                QPalette.ColorRole.Window: QColor("#232629"),
                QPalette.ColorRole.WindowText: QColor("#EFF0F1"),
                QPalette.ColorRole.Base: QColor("#1B1E20"),
                QPalette.ColorRole.AlternateBase: QColor("#252A2E"),
                QPalette.ColorRole.ToolTipBase: QColor("#31363B"),
                QPalette.ColorRole.ToolTipText: QColor("#EFF0F1"),
                QPalette.ColorRole.Text: QColor("#EFF0F1"),
                QPalette.ColorRole.Button: QColor("#31363B"),
                QPalette.ColorRole.ButtonText: QColor("#EFF0F1"),
                QPalette.ColorRole.BrightText: QColor("#FFFFFF"),
                QPalette.ColorRole.Highlight: QColor("#3DAEE9"),
                QPalette.ColorRole.HighlightedText: QColor("#FFFFFF"),
                QPalette.ColorRole.Link: QColor("#3DAEE9"),
                QPalette.ColorRole.LinkVisited: QColor("#9B7BD5"),
                QPalette.ColorRole.PlaceholderText: QColor("#A7AFB7"),
                QPalette.ColorRole.Light: QColor("#555B60"),
                QPalette.ColorRole.Midlight: QColor("#454A4F"),
                QPalette.ColorRole.Mid: QColor("#3D4246"),
                QPalette.ColorRole.Dark: QColor("#202326"),
                QPalette.ColorRole.Shadow: QColor("#111315"),
            }
            disabled = QColor("#70777D")
        else:
            colours = {
                QPalette.ColorRole.Window: QColor("#EFF0F1"),
                QPalette.ColorRole.WindowText: QColor("#232629"),
                QPalette.ColorRole.Base: QColor("#FFFFFF"),
                QPalette.ColorRole.AlternateBase: QColor("#F2F4F6"),
                QPalette.ColorRole.ToolTipBase: QColor("#FFFFDC"),
                QPalette.ColorRole.ToolTipText: QColor("#232629"),
                QPalette.ColorRole.Text: QColor("#232629"),
                QPalette.ColorRole.Button: QColor("#F7F7F8"),
                QPalette.ColorRole.ButtonText: QColor("#232629"),
                QPalette.ColorRole.BrightText: QColor("#FFFFFF"),
                QPalette.ColorRole.Highlight: QColor("#3DAEE9"),
                QPalette.ColorRole.HighlightedText: QColor("#FFFFFF"),
                QPalette.ColorRole.Link: QColor("#0068A6"),
                QPalette.ColorRole.LinkVisited: QColor("#6B4BA3"),
                QPalette.ColorRole.PlaceholderText: QColor("#6C757D"),
                QPalette.ColorRole.Light: QColor("#FFFFFF"),
                QPalette.ColorRole.Midlight: QColor("#E4E7E9"),
                QPalette.ColorRole.Mid: QColor("#B8BDC2"),
                QPalette.ColorRole.Dark: QColor("#92999F"),
                QPalette.ColorRole.Shadow: QColor("#687078"),
            }
            disabled = QColor("#9BA1A6")
        for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
            for role, colour in colours.items():
                base_palette.setColor(group, role, colour)
        for role, colour in colours.items():
            base_palette.setColor(QPalette.ColorGroup.Disabled, role, colour)
        for role in (
            QPalette.ColorRole.WindowText, QPalette.ColorRole.Text,
            QPalette.ColorRole.ButtonText, QPalette.ColorRole.PlaceholderText,
        ):
            base_palette.setColor(QPalette.ColorGroup.Disabled, role, disabled)
        return base_palette

    def apply_appimage_theme(self, theme, update_actions=True):
        """Apply System/Dark/Light chrome without touching document formatting."""
        if not self.appimage_theme_available or theme not in ("system","dark","light"):
            return
        application=QApplication.instance()
        if application is None:
            return
        # Markopad's exact implementation in every runtime: keep the active Qt
        # style, remove application QSS, reset to that style's standard palette,
        # then apply only the Dark/Light palette. Rico changes only the accent.
        application.setStyleSheet("")
        application.setPalette(application.style().standardPalette())
        if theme in ("dark","light"):
            application.setPalette(self._portable_markopad_palette(theme))
        if update_actions:
            for window in tuple(OPEN_WINDOWS):
                for selected,action in getattr(window,"appimage_theme_actions",{}).items():
                    action.blockSignals(True); action.setChecked(selected==theme); action.blockSignals(False)
                window.refresh_portable_icons()
                window.refresh_interface_theme()
                window.apply_editor_canvas_theme(update_action=True)
                window._schedule_interface_geometry_refresh()

    def set_appimage_theme(self, theme):
        """Persist System/Dark/Light application chrome across shipped runtimes."""
        theme=str(theme).strip().lower()
        if theme not in ("system","dark","light") or not self.appimage_theme_available:
            return
        os.environ.pop("RIQATONYPAD_APPIMAGE_THEME",None)
        for window in tuple(OPEN_WINDOWS):
            window.appimage_theme=theme
            window.appimage_theme_override=None
        self.apply_appimage_theme(theme)
        self.save_preferences()
        label="System" if theme=="system" else theme.title()
        self._show_status_message(f"Theme: {label}.",2500)

    def set_appimage_icon_set(self, icon_set):
        """Persist the Rico Harmony/Classic/Legacy command-icon family choice."""
        icon_set=str(icon_set).strip().lower()
        if icon_set not in ("new","classic","original","aero") or not self.appimage_theme_available:
            return
        os.environ.pop("RIQATONYPAD_APPIMAGE_ICONSET",None)
        for window in tuple(OPEN_WINDOWS):
            window.appimage_icon_set=icon_set
            window.appimage_icon_set_override=None
            for selected,action in getattr(window,"appimage_icon_actions",{}).items():
                action.blockSignals(True); action.setChecked(selected==icon_set); action.blockSignals(False)
            window.refresh_portable_icons()
        self.save_preferences()
        label={"new":"Harmony","classic":"Humility","original":"Heritage","aero":"Halcyon"}[icon_set]
        self._show_status_message(f"Riqa icons: {label}.",2500)

    def toggle_appimage_dark_mode(self, checked):
        """Compatibility hook for older shortcuts/configuration."""
        self.set_appimage_theme("dark" if checked else "light")
