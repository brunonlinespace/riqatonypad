#!/usr/bin/env python3
"""Existing RiqatonyPad quick tour presentation methods, relocated unchanged."""
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QCheckBox, QLabel, QPushButton, QVBoxLayout, QWizard, QWizardPage


def show_tutorial_wizard(self):
    if self.tutorial_dialog is not None:
        self.tutorial_dialog.show(); self.tutorial_dialog.raise_(); self.tutorial_dialog.activateWindow(); return
    wizard=QWizard(self); wizard.setWindowTitle("Quick Tour — RiqatonyPad"); wizard.setWindowIcon(self.windowIcon()); wizard.setModal(False); wizard.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose,True)
    wizard.setOption(QWizard.WizardOption.NoBackButtonOnStartPage,True)
    startup_checkbox=QCheckBox("Don't show Quick Tour on startup again",wizard); startup_checkbox.setChecked(bool(self.tutorial_seen))
    def set_tour_startup_disabled(checked):
        self.tutorial_seen=bool(checked); self.save_preferences()
    startup_checkbox.toggled.connect(set_tour_startup_disabled)
    wizard.setButton(QWizard.WizardButton.CustomButton1,startup_checkbox)
    wizard.setOption(QWizard.WizardOption.HaveCustomButton1,True)
    wizard.setButtonLayout([QWizard.WizardButton.CustomButton1,QWizard.WizardButton.Stretch,QWizard.WizardButton.BackButton,QWizard.WizardButton.NextButton,QWizard.WizardButton.FinishButton,QWizard.WizardButton.CancelButton])
    def add_page(title,body,button=None):
        page=QWizardPage(wizard); page.setTitle(title); layout=QVBoxLayout(page)
        label=QLabel(body,page); label.setWordWrap(True); label.setTextFormat(Qt.TextFormat.RichText); layout.addWidget(label)
        if button is not None: layout.addWidget(button,0,Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1); wizard.addPage(page)
    add_page("Welcome to RiqatonyPad","<p>RiqatonyPad is a lightweight Rich Text Format (.rtf) editor. Ribbon has five tabs: <b>File, Home, Insert, Configure and Help</b>, with Home open by default.</p><p>Hover a command for its name/shortcut. Use <b>Ctrl+Tab</b> and <b>Ctrl+Shift+Tab</b> to move between tabs. Double-click a tab title to collapse Ribbon controls; click a tab title once to reveal them again.</p>")
    add_page("Create, open and save","<p><b>File</b> contains New, Open, Save, Save As, Print, Export PDF and file-management commands. RiqatonyPad edits RTF only, so there is no private document format to choose.</p><p>Drag an RTF file onto the editor to follow your configured active-window/new-window behaviour.</p>")
    add_page("Format rich text","<p><b>Home</b> provides font face, size, paragraph style, emphasis, colours/highlights, bullets, indentation, alignment, paragraph settings and line spacing.</p><p><b>Insert</b> contains tables, links, symbols, images, horizontal rules, dates and times. Character formatting operates on the selection, or on the current word when there is no selection; whitespace changes the typing format for future text.</p>")
    add_page("Find and navigate","<p><b>Ctrl+F</b> opens the Find/Replace panel and focuses Find; press it again while Find has focus to close. <b>Ctrl+H</b> focuses Replace in the same panel and likewise closes it when Replace already has focus. <b>Esc</b> closes the panel. Use <b>F3</b> for the next result and <b>Shift+F3</b> for the previous result. The panel appears in the position selected under Editor Layout.</p><p>Locked Mode protects a document from accidental changes while navigation, copying and search remain available.</p><p>Help → Keyboard Shortcuts provides a live command inventory with menu filtering and fuzzy shortcut matching, including reordered modifiers and <b>Ctrl/Control/Ctl</b> aliases.</p>")
    add_page("View and reading comfort","<p><b>View</b> controls Full Screen, Show Status, Word Wrap, Dark Editor, Locked Mode, Editor Layout, Editor Toolbar, zoom and editor miscellany. The <b>Configure</b> Ribbon tab exposes the same standalone view/editor/theme/app settings in touch-friendly groups.</p><p>Ctrl+mouse-wheel zooms the document. Dark Editor changes only the editing surface; App Theme controls the rest of RiqatonyPad.</p>")
    add_page("Make it yours!","<p>Choose <b>Ribbon</b> or <b>Retro</b> from View → Editor Toolbar or Configure → Editor Settings. Retro uses the same shared command registry in one configurable 52×52 horizontal row; drag it with one finger or use the mouse wheel when it overflows. It deliberately has no toolbar overflow arrow.</p><p>Use <b>Customise Retro Bar…</b> for the full applicable command/selector inventory. New Document Defaults controls the exact font, size, style, line spacing and alignment used by future new documents.</p>")
    shortcuts_button=QPushButton("Open Keyboard Shortcuts…",wizard); shortcuts_button.setAutoDefault(False); shortcuts_button.clicked.connect(self.show_keyboard_shortcuts_dialog)
    add_page("RTF interoperability and help","<p>RiqatonyPad writes standards-based RTF intended to interoperate with other RTF applications. Bullet lists are stored with standard RTF list tables/overrides rather than RiqatonyPad-only markers.</p><p>Use <b>F1</b> for the bundled RTF Documentation. Help also provides GitHub, Raise an Issue, Keyboard Shortcuts and About.</p>",shortcuts_button)
    def tutorial_finished(_result):
        self.tutorial_dialog=None
        QTimer.singleShot(0,self._focus_editor_after_startup)
    wizard.finished.connect(tutorial_finished); self.tutorial_dialog=wizard; wizard.show(); wizard.raise_(); wizard.activateWindow()
