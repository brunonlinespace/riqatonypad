#!/usr/bin/env python3
# ==============================================================================
# RiqatonyPad - a lightweight cross-platform RTF editor
# Copyright (C) 2026 Bruno Machado
#
# GPLv3-or-later
#
# Version: 2.0.0
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
from widgets.rwpyn.character_count import count_visible_characters
from widgets.rwpyn.editor_preferences import EditorPreferencesMixin, MAX_CONFIG_FILE_SIZE, preference_bool, preference_text, resource_path
from editor_platform_startup import (
    OPEN_WINDOWS, register_window, normalise_windows_organisation_directory,
    platform_config_locations, configure_platform_identity, appimage_theme_resources,
)
import editor_platform_startup as _editor_platform_startup
from widgets.editor_ribbon_retro import EditorRibbonRetroMixin, RibbonScrollArea, RIBBON_BUTTON_SIZE, RIBBON_ICON_SIZE, RIBBON_FONT_FAMILY_WIDTH
from widgets.rwpyn.editor_lifecycle import EditorFileLifecycleMixin, MAX_FILE_SIZE, RTF_EXTENSIONS, DOCUMENT_EXTENSIONS
from widgets.editor_commands_appearance import EditorCommandsAppearanceMixin, RETRO_TOOLBAR_DEFAULT, COMMAND_SURFACE_SPECS, RETRO_TOOLBAR_ALLOWED
import widgets.editor_commands_appearance as _editor_commands_appearance
from widgets.rwpyn.editor_printing import EditorPrintingMixin, APP_NAME, fsync_directory, count_words
from widgets.rwpyn.editor_search_view import EditorSearchViewMixin, MAX_SEARCH_MATCHES
from widgets.rwpyn.editor_insertion import EditorInsertionMixin, read_bounded_bytes, host_process_environment, MAX_EMBEDDED_IMAGE_SIZE, MAX_IMAGE_SOURCE_SIZE, MAX_IMAGE_PIXELS
from widgets.rwpyn.editor_formatting import EditorFormattingMixin, FONT_SIZE_STEPS
from widgets.rwpyn.editor_widgets import (SafeTextDocument, RichTextEdit, MAX_PASTE_CHARACTERS,
    MAX_DOCUMENT_CHARACTERS, MAX_CLIPBOARD_HTML_CHARACTERS,
    RIQATONYPAD_INLINE_RICH_MIME, IMAGE_EXTENSIONS)
from rtf_new_document import NewDocumentDefaults, build_new_document_rtf_payload
from rtf_codec import (
    _qt_brush_colour, _rtf_clear_automatic_foreground,
    decode_rtf, document_to_rtf_with_properties, populate_qtextdocument_from_rtf_model,
    RTF_SYNTHETIC_STRUCTURE_BLOCK, RTF_TABLE_AUTOFIT_PROPERTY,
    RTF_AUTOMATIC_CONTRAST_PROPERTY,
    MAX_RTF_TABLE_ROWS, MAX_RTF_TABLE_COLUMNS, MAX_RTF_TABLE_CELLS,
)

APP_VERSION = "2.0.0"

# Canonical dual-interface profile. Ribbon remains the default; Retro is a
# persistent alternative presentation using the same command registry, shortcuts
# and bundled icon family. The registry is deliberately presentation-neutral:
# Ribbon chooses its two-row grouping while Retro exposes every applicable item
# through Customise Retro Bar.
import widgets.rwpyn.editor_preferences as _editor_preferences
_editor_preferences.RETRO_TOOLBAR_DEFAULT = RETRO_TOOLBAR_DEFAULT
_editor_preferences.RETRO_TOOLBAR_ALLOWED = RETRO_TOOLBAR_ALLOWED
import widgets.editor_ribbon_retro as _editor_ribbon_retro
_editor_ribbon_retro.RETRO_TOOLBAR_DEFAULT = RETRO_TOOLBAR_DEFAULT

_SMOKE_TEST_ARGUMENTS = {"--riqatonypad-smoke-test"}
_FORMAT_PARITY_ARGUMENTS = {"--riqatonypad-format-parity-probe"}
SMOKE_TEST_MODE = any(argument in _SMOKE_TEST_ARGUMENTS for argument in sys.argv[1:])
FORMAT_PARITY_PROBE_MODE = any(argument in _FORMAT_PARITY_ARGUMENTS for argument in sys.argv[1:])
# Consume RiqatonyPad's private test switches before QApplication sees filenames.
sys.argv[:] = [argument for argument in sys.argv if argument not in (_SMOKE_TEST_ARGUMENTS | _FORMAT_PARITY_ARGUMENTS)]
GITHUB_URL = "https://github.com/brunonlinespace/riqatonypad"
ISSUES_URL = GITHUB_URL + "/issues"

# Strong references to every open top-level editor window. This registry is
# independent of whichever window created another one, so closing a parent or
# intermediate window cannot cause another open document to be garbage
# collected without receiving its normal close/save prompt.

_editor_commands_appearance.OPEN_WINDOWS = OPEN_WINDOWS




























# ---------- Rich editor widgets ----------







# Existing dialog methods live in function-only UI modules; no new dialog classes.
import widgets.about_dialog as _about_dialog
import widgets.quick_tour as _quick_tour
import widgets.keyboard_shortcuts as _keyboard_shortcuts
_about_dialog.APP_NAME = APP_NAME
_about_dialog.APP_VERSION = APP_VERSION
_about_dialog.GITHUB_URL = GITHUB_URL
_about_dialog.resource_path = resource_path

class RiqatonyPad(EditorFileLifecycleMixin, EditorCommandsAppearanceMixin, EditorRibbonRetroMixin, EditorPreferencesMixin, EditorPrintingMixin, EditorSearchViewMixin, EditorFormattingMixin, EditorInsertionMixin, QMainWindow):
    show_about_dialog = _about_dialog.show_about_dialog
    show_tutorial_wizard = _quick_tour.show_tutorial_wizard
    show_keyboard_shortcuts_dialog = _keyboard_shortcuts.show_keyboard_shortcuts_dialog

    def __init__(self, initial_file=None):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        register_window(self)

        self.file_path = None
        self.file_format = "rtf"
        self.file_encoding = "rtf"
        self.file_bom = b""
        self.file_newline = "\n"
        self.file_disk_signature = None
        self._source_rtf_payload = None
        self._source_rtf_semantic_signature = None
        self.content_saved = True
        self._loading = False
        self._syncing_editors = False
        self.view_only = False
        self._view_only_prompt_shown = False
        self.rtf_compatibility_warnings = ()
        self.rtf_document_properties = {}
        self._rtf_save_warning_acknowledged = False
        self._search_refresh_suspended = False
        self.shortcuts_dialog = None
        self.about_dialog = None
        self.tutorial_dialog = None
        self.new_document_defaults_dialog = None
        self.search_matches = []
        self.search_results_truncated = False
        self.current_search_index = -1
        self.icon_bindings = []
        self.format_actions = []
        self.format_widgets = []
        self.visual_insert_actions = []
        self.editing_actions = []
        self.file_dependent_actions = []
        self.zoom_percent = 100
        self._visual_document_zoom_percent = 100
        self._visual_zoom_device = None
        self._skip_close_save_prompt = False
        self._external_change_pending = False
        self._backing_state = "normal"

        self.config_directory, self.config_import_candidates = platform_config_locations()
        self.config_file = os.path.join(self.config_directory, "riqatonypad.json")
        self.new_document_template_file = os.path.join(self.config_directory, "new-document-template.rtf")

        self.appimage_theme_files = appimage_theme_resources()
        self.appimage_theme_available = bool(self.appimage_theme_files)
        requested_theme = os.environ.get("RIQATONYPAD_APPIMAGE_THEME", "").strip().lower()
        self.appimage_theme_override = (
            requested_theme if requested_theme in ("system", "dark", "light") else None
        )
        requested_icon_set = os.environ.get("RIQATONYPAD_APPIMAGE_ICONSET", "").strip().lower()
        self.appimage_icon_set_override = (
            requested_icon_set if requested_icon_set in ("new", "classic", "original", "aero") else None
        )

        self.load_preferences()
        self.view_only = bool(self.persist_view_only)
        if self.appimage_theme_available:
            self.apply_appimage_theme(self.effective_appimage_theme(), update_actions=False)

        self.resize(980, 680)
        self.setMinimumSize(720, 500)
        self.setAcceptDrops(True)
        icon_path = resource_path("icons", "riqatonypad.png")
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.build_ui()
        self.bind_shortcuts()
        self._file_watcher = QFileSystemWatcher(self)
        self._file_watcher.fileChanged.connect(self._schedule_external_change_check)
        self._file_watcher.directoryChanged.connect(self._schedule_external_change_check)
        self._external_change_timer = QTimer(self)
        self._external_change_timer.setSingleShot(True)
        self._external_change_timer.setInterval(250)
        self._external_change_timer.timeout.connect(self._check_external_change_from_watcher)
        # Applying new-document defaults is programmatic startup work, not a
        # user edit.  Keep the untouched Untitled document at its clean save
        # point; if an initial-file import fails, this is also the clean
        # fallback document left behind.
        self._loading = True
        try:
            self.apply_preferences()
            self.visual_editor.document().setModified(False)
            self.content_saved = True
        finally:
            self._loading = False
        self.apply_native_style()
        self.update_title()
        self.update_status_counts()
        self.update_search_counter()
        self.update_formatting_state()

        if initial_file:
            self.load_file(initial_file, check_changes=False)

        if not self.tutorial_seen and not (SMOKE_TEST_MODE or FORMAT_PARITY_PROBE_MODE):
            QTimer.singleShot(0, self.show_tutorial_wizard)
        else:
            # Ribbon contains editable selectors; without an explicit post-show
            # focus handoff Qt may choose Font Size as the first focus widget.
            # Retro happened to avoid that path.  Put the caret on the document
            # after the event loop starts so both interfaces launch ready to type.
            QTimer.singleShot(0, self._focus_editor_after_startup)


    # ---------- Preferences ----------






    # ---------- UI ----------

    def build_ui(self):
        central = QWidget(self)
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(6)

        self.toolbar_stack = QWidget(self)
        self.toolbar_stack.setObjectName("toolbarStack")
        self.toolbar_stack_layout = QVBoxLayout(self.toolbar_stack)
        self.toolbar_stack_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_stack_layout.setSpacing(6)
        self.toolbar = QWidget(self.toolbar_stack)
        self.toolbar.setObjectName("toolbar")
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout.setSpacing(6)
        self.toolbar_stack_layout.addWidget(self.toolbar)

        self.app_menu_bar = self.menuBar()
        self.app_menu_bar.clear()
        self.make_file_menu(); self.make_edit_menu(); self.make_format_menu()
        self.make_insert_menu(); self.make_view_menu(); self.make_settings_menu(); self.make_help_menu()

        self.menu_buttons_container = QWidget(self.toolbar)
        self.menu_buttons_layout = QHBoxLayout(self.menu_buttons_container)
        self.menu_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_buttons_layout.setSpacing(6)
        self.menu_buttons_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.menu_buttons = []
        for label, menu in (("File",self.file_menu),("Edit",self.edit_menu),("Format",self.format_menu),("Insert",self.insert_menu),("View",self.view_menu),("Settings",self.settings_menu),("Help",self.help_menu)):
            button=QToolButton(self.menu_buttons_container); button.setText(label)
            button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            button.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
            button.setMenu(menu); self.menu_buttons_layout.addWidget(button); self.menu_buttons.append(button)
        self.primary_controls=QWidget(self.toolbar)
        self.primary_controls.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Preferred)
        primary_layout=QHBoxLayout(self.primary_controls); primary_layout.setContentsMargins(0,0,0,0); primary_layout.setSpacing(6)
        primary_layout.addWidget(self.menu_buttons_container)
        self.toolbar_layout.addWidget(self.primary_controls,0,Qt.AlignmentFlag.AlignLeft)

        # Unified transient Find/Replace panel. It remains the same movable
        # search_container used by RiqatonyPad's four Editor Layout modes, so Ribbon
        # versus Retro and top/bottom placement stay independent of search UX.
        self.search_container=QFrame(central); self.search_container.setObjectName("searchContainer")
        self.search_container.setFrameShape(QFrame.Shape.StyledPanel)
        self.search_container.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        search_layout=QGridLayout(self.search_container); search_layout.setContentsMargins(8,6,8,6); search_layout.setHorizontalSpacing(6); search_layout.setVerticalSpacing(4)
        self.search_entry=QLineEdit(self.search_container); self.search_entry.setPlaceholderText("Find")
        self.replace_entry=QLineEdit(self.search_container); self.replace_entry.setPlaceholderText("Replace")
        self.search_case_checkbox=QCheckBox("Match case",self.search_container)
        self.search_count_label=QLabel("",self.search_container); self.search_count_label.setMinimumWidth(54); self.search_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.search_previous_button=QPushButton("Previous",self.search_container)
        self.search_next_button=QPushButton("Next",self.search_container)
        self.search_replace_button=QPushButton("Replace",self.search_container)
        self.search_replace_all_button=QPushButton("Replace All",self.search_container)
        self.search_close_button=QPushButton("Close",self.search_container)
        search_layout.addWidget(self.search_entry,0,0,1,3)
        search_layout.addWidget(self.search_previous_button,0,3)
        search_layout.addWidget(self.search_next_button,0,4)
        search_layout.addWidget(self.search_case_checkbox,0,5)
        search_layout.addWidget(self.search_count_label,0,6)
        search_layout.addWidget(self.replace_entry,1,0,1,3)
        search_layout.addWidget(self.search_replace_button,1,3)
        search_layout.addWidget(self.search_replace_all_button,1,4)
        search_layout.addWidget(self.search_close_button,1,6)
        self.search_entry.textChanged.connect(self.refresh_search)
        self.search_case_checkbox.toggled.connect(self.refresh_search)
        self.search_entry.returnPressed.connect(self.find_next)
        self.search_previous_button.clicked.connect(self.find_previous)
        self.search_next_button.clicked.connect(self.find_next)
        self.search_replace_button.clicked.connect(self.replace_next)
        self.search_replace_all_button.clicked.connect(self.replace_all)
        self.search_close_button.clicked.connect(self.hide_find_panel)
        self.replace_find_entry=self.search_entry
        self.replace_with_entry=self.replace_entry
        self.replace_case_checkbox=self.search_case_checkbox
        self.search_container.hide()

        self.format_toolbar=QWidget(self.toolbar_stack); self.format_toolbar.setObjectName("formatToolbar")
        format_layout=QVBoxLayout(self.format_toolbar); format_layout.setContentsMargins(0,0,0,0); format_layout.setSpacing(4)
        format_top_layout=QHBoxLayout(); format_top_layout.setSpacing(5)
        format_bottom_layout=QHBoxLayout(); format_bottom_layout.setSpacing(5)
        self.font_combo=QFontComboBox(self.format_toolbar); self.font_combo.setMaximumWidth(175); self.font_combo.setToolTip("Font family"); self.font_combo.setEditable(True); self.font_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        if self.font_combo.lineEdit() is not None:
            e=self.font_combo.lineEdit(); e.setReadOnly(True); e.setFocusPolicy(Qt.FocusPolicy.NoFocus); e.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.font_combo.currentTextChanged.connect(self._reset_font_face_display); self.font_combo.currentFontChanged.connect(self.set_selected_font); self.font_combo.currentFontChanged.connect(lambda _font:self._reset_font_face_display())
        format_top_layout.addWidget(self.font_combo)
        self.font_size_combo=QComboBox(self.format_toolbar); self.font_size_combo.setEditable(True); self.font_size_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert); self.font_size_combo.setMaximumWidth(68); self.font_size_combo.addItems(["8","9","10","11","12","14","16","18","20","24","28","32","36","48","72"]); self.font_size_combo.currentTextChanged.connect(self.set_selected_font_size); format_top_layout.addWidget(self.font_size_combo)
        self.font_weight_combo=QComboBox(self.format_toolbar)
        for text,weight in (("Thin",QFont.Weight.Thin),("Extra Light",QFont.Weight.ExtraLight),("Light",QFont.Weight.Light),("Regular",QFont.Weight.Normal),("Medium",QFont.Weight.Medium),("Demi Bold",QFont.Weight.DemiBold),("Bold",QFont.Weight.Bold),("Extra Bold",QFont.Weight.ExtraBold),("Black",QFont.Weight.Black)):
            self.font_weight_combo.addItem(text,int(weight))
        self.font_weight_combo.currentIndexChanged.connect(self.apply_font_weight_from_combo); format_top_layout.addWidget(self.font_weight_combo)
        self.heading_combo=QComboBox(self.format_toolbar); self.heading_combo.setMaximumWidth(118)
        for text,level in (("Normal",0),("Heading 1",1),("Heading 2",2),("Heading 3",3),("Heading 4",4),("Heading 5",5),("Heading 6",6)): self.heading_combo.addItem(text,level)
        self.heading_combo.setToolTip("Font Style — Normal Ctrl+Shift+0; Headings 1–6 Ctrl+Shift+1…6"); self.heading_combo.currentIndexChanged.connect(self.apply_heading_from_combo); format_top_layout.addWidget(self.heading_combo)
        def tool(target_layout,text,tip,callback,checkable=False):
            button=QToolButton(self.format_toolbar); button.setText(text); button.setToolTip(tip); button.setFocusPolicy(Qt.FocusPolicy.NoFocus); button.setCheckable(checkable); button.clicked.connect(callback); target_layout.addWidget(button); self.format_widgets.append(button); return button
        self.bold_button=tool(format_top_layout,"B","Bold (Ctrl+B)",self.toggle_bold,True); f=self.bold_button.font(); f.setBold(True); self.bold_button.setFont(f)
        self.italic_button=tool(format_top_layout,"I","Italic (Ctrl+I)",self.toggle_italic,True); f=self.italic_button.font(); f.setItalic(True); self.italic_button.setFont(f)
        self.underline_button=tool(format_top_layout,"U","Underline (Ctrl+U)",self.toggle_underline,True); f=self.underline_button.font(); f.setUnderline(True); self.underline_button.setFont(f)
        self.strike_button=tool(format_top_layout,"S","Strikethrough (Ctrl+Shift+X)",self.toggle_strikethrough,True); f=self.strike_button.font(); f.setStrikeOut(True); self.strike_button.setFont(f)
        self.text_colour_button=tool(format_top_layout,"A▾","Text Colour (Ctrl+Shift+C)",self.choose_text_colour)
        self.highlight_button=tool(format_top_layout,"▣","Highlight Colour (Ctrl+Shift+H)",self.choose_highlight_colour)
        format_top_layout.addStretch(1); format_layout.addLayout(format_top_layout)
        sep=QFrame(self.format_toolbar); sep.setFrameShape(QFrame.Shape.HLine); sep.setFrameShadow(QFrame.Shadow.Sunken); format_layout.addWidget(sep)
        self.align_left_button=tool(format_bottom_layout,"L","Align Left (Ctrl+L)",lambda:self.set_alignment(Qt.AlignmentFlag.AlignLeft),True)
        self.align_center_button=tool(format_bottom_layout,"C","Align Centre (Ctrl+E)",lambda:self.set_alignment(Qt.AlignmentFlag.AlignHCenter),True)
        self.align_right_button=tool(format_bottom_layout,"R","Align Right (Ctrl+R)",lambda:self.set_alignment(Qt.AlignmentFlag.AlignRight),True)
        self.align_justify_button=tool(format_bottom_layout,"J","Justify (Ctrl+J)",lambda:self.set_alignment(Qt.AlignmentFlag.AlignJustify),True)
        self.bullet_button=tool(format_bottom_layout,"•","Bullet List (Ctrl+Shift+L)",self.toggle_bullet_list,True)
        self.symbols_button=tool(format_bottom_layout,"†","Symbol",self.show_symbols_popup)
        self.indent_button=tool(format_bottom_layout,"→","Indent (Ctrl+])",lambda:self.change_indent(1)); self.outdent_button=tool(format_bottom_layout,"←","Outdent (Ctrl+[)",lambda:self.change_indent(-1))
        self.line_spacing_combo=QComboBox(self.format_toolbar)
        for label,value in (("1",100),("1.15",115),("1.5",150),("2",200)): self.line_spacing_combo.addItem(label,value)
        self.line_spacing_combo.setToolTip("Line Spacing — 1.0 Ctrl+1; 1.15 Ctrl+2; 1.5 Ctrl+3; 2.0 Ctrl+4"); self.line_spacing_combo.currentIndexChanged.connect(self.apply_line_spacing_from_combo); format_bottom_layout.addWidget(self.line_spacing_combo); format_bottom_layout.addStretch(1); format_layout.addLayout(format_bottom_layout)
        self.format_widgets.extend([self.font_combo,self.font_size_combo,self.font_weight_combo,self.heading_combo,self.line_spacing_combo,self.text_colour_button,self.highlight_button])
        self.toolbar_stack_layout.addWidget(self.format_toolbar)

        self.external_banner=QFrame(central); self.external_banner.setObjectName("externalChangeBanner"); self.external_banner.setFrameShape(QFrame.Shape.StyledPanel)
        external_banner_layout=QHBoxLayout(self.external_banner); external_banner_layout.setContentsMargins(8,6,8,6); external_banner_layout.setSpacing(8)
        self.external_label=QLabel("This file changed on disk after it was opened.",self.external_banner); self.external_label.setWordWrap(True); external_banner_layout.addWidget(self.external_label,1)
        self.external_reload_button=QPushButton("Reload from Disk",self.external_banner); self.external_reload_button.clicked.connect(self._reload_external_change); external_banner_layout.addWidget(self.external_reload_button)
        self.external_save_version_button=QPushButton("Save Version As…",self.external_banner); self.external_save_version_button.clicked.connect(self._save_version_as); external_banner_layout.addWidget(self.external_save_version_button)
        self.external_banner.hide()

        self.visual_editor=RichTextEdit(self); self.visual_editor.viewport().installEventFilter(self); self.visual_editor.setObjectName("visualEditor"); self.visual_editor.setAcceptRichText(True); self.visual_editor.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoNone); self.visual_editor.setFrameShape(QFrame.Shape.NoFrame); self.visual_editor.setContentsMargins(0,0,0,0); self.visual_editor.setViewportMargins(0,0,0,0); self.visual_editor.document().setDocumentMargin(4.0)
        self.visual_editor.currentCharFormatChanged.connect(self.update_formatting_state); self.visual_editor.cursorPositionChanged.connect(self.update_formatting_state); self.visual_editor.document().modificationChanged.connect(self.on_modification_changed); self.visual_editor.textChanged.connect(self.on_document_text_changed); self.visual_editor.installEventFilter(self)
        self.text_area=self.visual_editor
        self.main_layout.addWidget(self.toolbar_stack); self.main_layout.addWidget(self.external_banner); self.main_layout.addWidget(self.visual_editor,1)

        self.app_status_bar=self.statusBar(); self.app_status_bar.setObjectName("riqatonypadEditorStatus"); self.app_status_bar.setSizeGripEnabled(False)
        self.status_message_label=QLabel("",self.app_status_bar); self.status_message_label.setMinimumWidth(0); self.status_message_label.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred); self.status_message_label.setToolTip("")
        self.status_indicators_label=QLabel("Insert · Chars 0 · 100%",self.app_status_bar)
        self.status_indicators_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.status_indicators_label.setMinimumWidth(0)
        self._status_message_timer=QTimer(self); self._status_message_timer.setSingleShot(True); self._status_message_timer.timeout.connect(self._clear_status_message)
        self.app_status_bar.addWidget(self.status_message_label,1); self.app_status_bar.addPermanentWidget(self.status_indicators_label)
        self.build_ribbon(); self.build_retro_toolbar()













































        # The action remains available to the Help ribbon and platform roles.
        # The action remains available to the Help ribbon and platform roles.






    def set_dirty_duplicate_action(self, choice):
        if choice not in ("ask", "current", "saved"):
            return
        self.dirty_duplicate_action = choice
        for selected, action in getattr(self, "dirty_duplicate_actions", {}).items():
            action.setChecked(selected == choice)
        self.save_preferences()

    def set_dirty_external_action(self, choice):
        if choice not in ("ask", "save", "saved"):
            return
        self.dirty_external_action = choice
        for selected, action in getattr(self, "dirty_external_actions", {}).items():
            action.setChecked(selected == choice)
        self.save_preferences()


    def _focus_editor_after_startup(self):
        """Give normal startup focus to the document after Ribbon is shown."""
        if not hasattr(self, "visual_editor") or not self.visual_editor.isEnabled():
            return
        # Do not steal focus from a first-run/tutorial window.
        if self.tutorial_dialog is not None and self.tutorial_dialog.isVisible():
            return
        self.visual_editor.setFocus(Qt.FocusReason.OtherFocusReason)
        self.visual_editor.ensureCursorVisible()


    def toggle_view_only(self, checked):
        checked=bool(checked)
        if not checked and self.view_only and self.confirm_locked_mode_disable:
            dialog=QMessageBox(self); dialog.setWindowTitle("Disable Locked Mode? — RiqatonyPad"); dialog.setIcon(QMessageBox.Icon.Warning); dialog.setText("Locked Mode protects files from accidental changes."); dialog.setInformativeText("Continue only when you intend to edit the document.")
            dont_ask=QCheckBox("Don't ask again when disabling Locked Mode",dialog); dialog.setCheckBox(dont_ask)
            keep=dialog.addButton("Keep Locked",QMessageBox.ButtonRole.RejectRole); cont=dialog.addButton("Continue",QMessageBox.ButtonRole.AcceptRole); dialog.setDefaultButton(keep); dialog.setEscapeButton(keep); dialog.exec()
            if dialog.clickedButton() is not cont:
                self.view_only_action.blockSignals(True); self.view_only_action.setChecked(True); self.view_only_action.blockSignals(False); return
            if dont_ask.isChecked(): self.confirm_locked_mode_disable=False
        self.view_only=checked; self.persist_view_only=checked; self._view_only_prompt_shown=False; self.view_only_action.blockSignals(True); self.view_only_action.setChecked(checked); self.view_only_action.blockSignals(False); self._update_mode_capabilities(); self.update_title(); self.update_status_counts(); self.save_preferences(); self._show_status_message("Locked Mode enabled." if checked else "Locked Mode disabled.",3000)

    def explain_view_only_block(self):
        self._show_status_message("Editing is disabled while Locked Mode is enabled.",4000)
        if self._view_only_prompt_shown: return
        self._view_only_prompt_shown=True
        QMessageBox.information(self,"Locked Mode — RiqatonyPad","Editing is disabled because Locked Mode is enabled.\n\nClear View → Locked Mode and confirm Continue to edit the document.")


    def eventFilter(self, watched, event):
        retro_toolbar=getattr(self,"retro_toolbar",None)
        if retro_toolbar is not None and watched is retro_toolbar and event.type() in (QEvent.Type.Resize,QEvent.Type.Show,QEvent.Type.LayoutRequest,QEvent.Type.StyleChange,QEvent.Type.FontChange):
            self._schedule_interface_geometry_refresh()
        ribbon_tabs=getattr(self,"ribbon_tabs",None)
        if ribbon_tabs is not None and watched is ribbon_tabs and event.type() in (QEvent.Type.Resize,QEvent.Type.Show,QEvent.Type.LayoutRequest,QEvent.Type.StyleChange,QEvent.Type.FontChange):
            self._schedule_interface_geometry_refresh()
        if ribbon_tabs is not None and watched is ribbon_tabs.tabBar():
            if event.type()==QEvent.Type.MouseButtonPress and getattr(self,"_ribbon_collapsed",False) and event.button()==Qt.MouseButton.LeftButton:
                idx=ribbon_tabs.tabBar().tabAt(event.position().toPoint())
                if idx>=0: ribbon_tabs.setCurrentIndex(idx); self.set_ribbon_collapsed(False); return True
            if event.type()==QEvent.Type.MouseButtonDblClick and not getattr(self,"_ribbon_collapsed",False) and event.button()==Qt.MouseButton.LeftButton and ribbon_tabs.tabBar().tabAt(event.position().toPoint())>=0:
                self.set_ribbon_collapsed(True); return True
            if event.type()==QEvent.Type.Wheel:
                delta=event.angleDelta().y() or event.angleDelta().x()
                if delta: self.cycle_ribbon_tab(-1 if delta>0 else 1); return True
        if bool(watched.property("riqatonypad_instant_tooltip")):
            if event.type()==QEvent.Type.Enter and watched.toolTip(): QToolTip.showText(watched.mapToGlobal(watched.rect().bottomLeft()),watched.toolTip(),watched,watched.rect(),7000)
            elif event.type()==QEvent.Type.Leave: QToolTip.hideText()
            elif event.type()==QEvent.Type.Wheel:
                retro=getattr(self,"retro_toolbar",None)
                if retro is not None and retro.isVisible() and isinstance(retro,RibbonScrollArea) and retro.pan_from_wheel_event(event): return True
                scroll=ribbon_tabs.currentWidget() if ribbon_tabs is not None else None
                if isinstance(scroll,RibbonScrollArea) and scroll.pan_from_wheel_event(event): return True
        editor=getattr(self,"visual_editor",None)
        viewport=editor.viewport() if editor is not None else None
        if watched is viewport and event.type() in (QEvent.Type.DragEnter,QEvent.Type.DragMove,QEvent.Type.Drop):
            mime=event.mimeData()
            local_files=[url.toLocalFile() for url in mime.urls() if url.isLocalFile() and os.path.isfile(url.toLocalFile())] if mime.hasUrls() else []
            if local_files:
                event.acceptProposedAction()
                if event.type()==QEvent.Type.Drop:
                    images=[path for path in local_files if Path(path).suffix.lower() in IMAGE_EXTENSIONS]
                    documents=[path for path in local_files if path not in images]
                    for path in images: self.insert_image_path(path)
                    if documents: QTimer.singleShot(0,lambda paths=list(documents):self.open_dropped_files(paths))
                return True
        if watched is editor and event.type()==QEvent.Type.KeyPress and event.key()==Qt.Key.Key_Insert:
            editor.setOverwriteMode(not editor.overwriteMode()); self.update_status_counts()
            self._show_status_message("Overwrite mode enabled." if editor.overwriteMode() else "Insert mode enabled.", 2500)
            return True
        if self.view_only and watched is editor:
            if event.type()==QEvent.Type.InputMethod and (event.commitString() or event.preeditString()): self.explain_view_only_block(); return True
            if event.type()==QEvent.Type.KeyPress:
                modifiers=event.modifiers(); mutating=event.key() in {Qt.Key.Key_Backspace,Qt.Key.Key_Delete,Qt.Key.Key_Return,Qt.Key.Key_Enter,Qt.Key.Key_Tab}; printable=bool(event.text()) and not (modifiers&(Qt.KeyboardModifier.ControlModifier|Qt.KeyboardModifier.AltModifier|Qt.KeyboardModifier.MetaModifier)); standard=any(event.matches(k) for k in (QKeySequence.StandardKey.Cut,QKeySequence.StandardKey.Paste,QKeySequence.StandardKey.Undo,QKeySequence.StandardKey.Redo))
                if mutating or printable or standard: self.explain_view_only_block(); return True
        return super().eventFilter(watched,event)













    def _new_document_alignment_flag(self):
        return {
            "left": Qt.AlignmentFlag.AlignLeft,
            "centre": Qt.AlignmentFlag.AlignHCenter,
            "right": Qt.AlignmentFlag.AlignRight,
            "justify": Qt.AlignmentFlag.AlignJustify,
        }.get(self.new_document_alignment, Qt.AlignmentFlag.AlignLeft)










    # ---------- Editing ----------





    # ---------- Rich-text editing ----------
    def document_editing_available(self, show_message=True):
        """Return whether document mutation is allowed in the active window."""
        if not self.view_only:
            return True
        if show_message:
            self.explain_view_only_block()
        return False


    def visual_editing_available(self, show_message=True):
        return self.document_editing_available(show_message)













































































































    def toggle_fullscreen(self, checked):
        self.showFullScreen() if bool(checked) else self.showNormal()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type()==QEvent.Type.WindowStateChange and hasattr(self,"fullscreen_action"):
            self.fullscreen_action.blockSignals(True); self.fullscreen_action.setChecked(self.isFullScreen()); self.fullscreen_action.blockSignals(False)

    def toggle_status_bar(self, checked):
        self.show_status_bar = bool(checked)
        self.app_status_bar.setVisible(self.show_status_bar)
        if self.show_status_bar:
            self.update_status_counts()
        self.save_preferences()

    def toggle_menu_style(self, checked):
        """Compatibility hook retained for older configuration imports."""
        self.use_app_menu = False
        self.app_menu_bar.setVisible(False)

    def apply_menu_style(self):
        self.use_app_menu = False
        self.app_menu_bar.setVisible(False)

    def set_drop_open_mode(self, mode):
        if mode not in ("active_window", "new_window"):
            return
        self.drop_open_mode = mode
        for value, action in self.drop_behaviour_actions.items():
            action.blockSignals(True)
            action.setChecked(value == mode)
            action.blockSignals(False)
        self._sync_app_drag_drop_menu_icon()
        self.save_preferences()

    def apply_native_style(self):
        """Keep source/portable chrome system-native; editor canvas stays independent."""
        self.setStyleSheet("")
        self.apply_editor_canvas_theme(update_action=True)

    # ---------- Printing / Help ----------






















    def _documentation_path(self):
        candidates = (
            Path(resource_path("docs", "RiqatonyPad-Documentation.rtf")),
            Path(__file__).resolve().parent / "docs" / "RiqatonyPad-Documentation.rtf",
        )
        appdir = os.environ.get("APPDIR")
        if appdir:
            candidates += (
                Path(appdir) / "usr" / "share" / "doc" / "riqatonypad" / "RiqatonyPad-Documentation.rtf",
            )
        for candidate in candidates:
            try:
                if candidate.is_file():
                    return candidate.resolve()
            except OSError:
                continue
        return None

    def open_documentation(self):
        """Open bundled RTF documentation in a separate RiqatonyPad window."""
        path = self._documentation_path()
        if path is None:
            QMessageBox.information(
                self,
                "Documentation — RiqatonyPad",
                "The bundled RiqatonyPad-Documentation.rtf file could not be found.",
            )
            return False
        window = self.new_window(str(path), show=False)
        # Documentation is a showcase RTF document, not an editable installed
        # resource. Keep it read-only without changing the user's persisted
        # Locked Mode preference for normal documents. When Ribbon is active,
        # start this one documentation window collapsed without changing the
        # user's normal persisted Ribbon preference. Retro has no collapsed state.
        window.view_only = True
        window._view_only_prompt_shown = False
        if window.interface_style == "ribbon":
            window.set_ribbon_collapsed(True, persist=False)
        window._update_mode_capabilities()
        window.update_title()
        window._show_status_message(
            "Bundled RiqatonyPad documentation — use Save As to make an editable copy.",
            5000,
        )
        window.show()
        return True

    def _open_host_target(self, target, *, local=False):
        """Open a URL/path with the host desktop, outside AppImage Qt/library env."""
        target=str(target)
        environment=host_process_environment(); host_path=environment.get("PATH")
        if sys.platform=="win32":
            try:
                os.startfile(target)
                return True
            except (AttributeError,OSError):
                pass
        candidates=[]
        if sys.platform=="darwin":
            candidates=[("open",[target])]
        elif sys.platform!="win32":
            candidates=[("xdg-open",[target]),("gio",["open",target])]
        for command,args in candidates:
            executable=shutil.which(command,path=host_path)
            if not executable:
                continue
            try:
                subprocess.Popen([executable,*args],env=environment,start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                return True
            except OSError:
                continue
        url=QUrl.fromLocalFile(target) if local else QUrl(target)
        return bool(QDesktopServices.openUrl(url))

    def open_document_link(self, href):
        href=str(href or "").strip()
        if not href or not is_safe_link_target(href):
            return False
        if href.startswith("#"):
            try:
                self.visual_editor.scrollToAnchor(href[1:])
                self.visual_editor.setFocus()
                return True
            except Exception:
                return False
        parsed=QUrl(href)
        if parsed.scheme().lower() in ("http","https","mailto"):
            return self._open_host_target(href)
        if parsed.isLocalFile():
            path=parsed.toLocalFile()
        else:
            base=os.path.dirname(os.path.abspath(self.file_path)) if self.file_path else os.getcwd()
            path=os.path.abspath(os.path.join(base,href))
        if os.path.exists(path):
            return self._open_host_target(path,local=True)
        self._show_status_message("The linked file could not be found.",4000)
        return False

    def open_github_repository(self):
        opened=self._open_host_target(GITHUB_URL)
        if not opened: QMessageBox.warning(self,"GitHub Repository — RiqatonyPad","The host desktop could not open the repository URL.")
        return opened

    def report_an_issue(self):
        opened=self._open_host_target(ISSUES_URL)
        if not opened: QMessageBox.warning(self,"Raise an Issue — RiqatonyPad","The host desktop could not open the issue-report URL.")
        return opened



    def show_format_support_dialog(self):
        QMessageBox.information(self,"RTF Support — RiqatonyPad","RiqatonyPad edits Rich Text Format (.rtf) only.\n\nSupported core: fonts and character formatting, colours/highlights, paragraphs, lists, hyperlinks, embedded PNG/JPEG images, horizontal rules and bounded simple non-nested tables.\n\nUnsupported or partially supported constructs such as OLE objects, shapes, comments, footnotes, headers/footers and nested tables are reported in Properties and warned before a destructive save.\n\nPrint and Export PDF are output operations; RiqatonyPad is not a PDF reader.")


    # ---------- Files ----------

    def update_title(self):
        prefix="*" if not self.content_saved else ""
        name=os.path.basename(self.file_path) if self.file_path else "Untitled.rtf"
        folder=""
        if self.file_path:
            parent=Path(os.path.abspath(self.file_path)).parent
            folder=parent.name or str(parent)
        scope=f" — {folder}" if folder else ""
        suffix=" — Locked Mode" if self.view_only else ""
        self.setWindowTitle(f"{prefix}{name}{scope} — RiqatonyPad{suffix}")


    def on_modification_changed(self, _modified):
        if self._loading or self._syncing_editors:
            return
        active_modified = self.text_area.document().isModified()
        self.content_saved = not active_modified
        self.update_title()


    def _clear_status_message(self):
        self._critical_editor_message = False
        self._critical_editor_message_kind = None
        if hasattr(self,"status_message_label"):
            self.status_message_label.clear(); self.status_message_label.setToolTip("")

    def _show_status_message(self, message, timeout=4000, *, warning_kind=None):
        from riqatony_pad.widgets.message_conventions import (
            DEFAULT_MESSAGE_DURATION_MS, is_critical_status, status_sentence,
        )
        if not hasattr(self,"status_message_label"):
            return
        text = status_sentence(message)
        critical = is_critical_status(text)
        recovering = text.startswith(("Loaded ", "Saved ", "Saved as ", "Saved RiqatonyPad version as ", "Deleted "))
        if getattr(self, "_critical_editor_message", False) and not (critical or recovering):
            return
        self._critical_editor_message = critical
        self._critical_editor_message_kind = warning_kind if critical else None
        self.status_message_label.setText(text)
        self.status_message_label.setToolTip(text)
        self._status_message_timer.stop()
        if not critical:
            self._status_message_timer.start(DEFAULT_MESSAGE_DURATION_MS)

    def update_status_counts(self):
        if not hasattr(self,"text_area"): return
        mode="Overwrite" if self.text_area.overwriteMode() else "Insert"
        characters=count_visible_characters(self.text_area.document())
        self.status_indicators_label.setText(f"{mode} · Chars {characters:,} · {self.zoom_percent}%")




















    # ---------- Document formats and durable file I/O ----------





    def _update_mode_capabilities(self):
        editing=not self.view_only
        self.visual_editor.setAcceptRichText(True); self.visual_editor.setReadOnly(self.view_only)
        if hasattr(self,"format_ribbon_group"): self.format_ribbon_group.setEnabled(editing)
        if hasattr(self,"paragraph_ribbon_group"): self.paragraph_ribbon_group.setEnabled(editing)
        self.format_menu.setEnabled(editing)
        for action in self.format_actions: action.setEnabled(editing)
        for widget in self.format_widgets: widget.setEnabled(editing)
        for widget in getattr(self,"retro_format_widgets",()): widget.setEnabled(editing)
        for action in self.visual_insert_actions: action.setEnabled(editing)
        for action in self.editing_actions: action.setEnabled(editing)
        for action in self.file_dependent_actions: action.setEnabled(bool(self.file_path))
        self.copy_action.setEnabled(True); self.select_all_action.setEnabled(True)
        if hasattr(self,"table_edit_actions"):
            in_table=editing and self.visual_editor.textCursor().currentTable() is not None
            for action in self.table_edit_actions: action.setEnabled(in_table)
        if hasattr(self,"edit_link_action"):
            in_link=editing and self._visual_anchor_cursor() is not None; self.edit_link_action.setEnabled(in_link); self.remove_link_action.setEnabled(in_link)
        self.view_only_action.blockSignals(True); self.view_only_action.setChecked(self.view_only); self.view_only_action.blockSignals(False)




















    def new_window(self, file_path=None, *, show=True):
        """Open an independently managed RiqatonyPad window in this Qt process."""
        if isinstance(file_path, bool):
            file_path = None
        window = RiqatonyPad(file_path)
        if show:
            window.show()
        return window




















    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(url.isLocalFile() for url in event.mimeData().urls()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [
            url.toLocalFile() for url in event.mimeData().urls()
            if url.isLocalFile() and os.path.isfile(url.toLocalFile())
        ]
        if not files:
            return
        images = [path for path in files if Path(path).suffix.lower() in IMAGE_EXTENSIONS]
        documents = [path for path in files if path not in images]
        for image in images:
            self.insert_image_path(image)
        if documents:
            self.open_dropped_files(documents)
        event.acceptProposedAction()


    def closeEvent(self, event):
        if self._skip_close_save_prompt:
            self._skip_close_save_prompt = False
            event.accept()
            return
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()




def main():
    """Launch with the same host-owned startup bindings as the original entry point."""
    _editor_platform_startup.RiqatonyPad = RiqatonyPad
    _editor_platform_startup.APP_VERSION = APP_VERSION
    _editor_platform_startup.SMOKE_TEST_MODE = SMOKE_TEST_MODE
    _editor_platform_startup.FORMAT_PARITY_PROBE_MODE = FORMAT_PARITY_PROBE_MODE
    _editor_platform_startup.configure_platform_identity = configure_platform_identity
    _editor_platform_startup.resource_path = resource_path
    return _editor_platform_startup.main()


if __name__ == "__main__":
    main()
