#!/usr/bin/env python3
# RiqatonyPad standalone platform and startup support, extracted from 2.0.0-x8.0.
# The existing function bodies below are unchanged.
import os
import sys
import hashlib
from PyQt6.QtCore import QEvent, QSize, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextListFormat
from PyQt6.QtWidgets import QApplication, QFontComboBox, QToolButton
from widgets.rwpyn.editor_printing import APP_NAME
from widgets.rwpyn.editor_preferences import resource_path
from widgets.editor_ribbon_retro import RibbonScrollArea, RIBBON_BUTTON_SIZE, RIBBON_FONT_FAMILY_WIDTH

OPEN_WINDOWS = set()
# Startup is invoked through the original host, which supplies its live class
# and launch-mode flags. These bindings never create another application window.
RiqatonyPad = None
APP_VERSION = None
SMOKE_TEST_MODE = False
FORMAT_PARITY_PROBE_MODE = False

def register_window(window):
    """Keep a top-level editor alive until Qt destroys that exact window."""
    OPEN_WINDOWS.add(window)
    window.destroyed.connect(
        lambda _object=None, registered=window: OPEN_WINDOWS.discard(registered)
    )



def normalise_windows_organisation_directory(appdata):
    """Migrate the earlier organisation directory spelling without data loss."""
    desired_name = "brunonlinespace"
    desired_path = os.path.join(appdata, desired_name)
    legacy_names = ("BrunoOnlineSpace", "brunoonlinespace")

    try:
        entries = list(os.scandir(appdata))
    except OSError:
        return desired_path

    if any(
        entry.is_dir(follow_symlinks=False) and entry.name == desired_name
        for entry in entries
    ):
        return desired_path

    legacy_entry = next(
        (
            entry for entry in entries
            if entry.is_dir(follow_symlinks=False) and entry.name in legacy_names
        ),
        None,
    )
    if legacy_entry is None:
        return desired_path

    temporary_path = None
    for counter in range(100):
        candidate = os.path.join(
            appdata,
            f".riqatonypad-org-migration-{os.getpid()}-{counter}",
        )
        if not os.path.exists(candidate):
            temporary_path = candidate
            break
    if temporary_path is None:
        return desired_path

    try:
        os.rename(legacy_entry.path, temporary_path)
        os.rename(temporary_path, desired_path)
    except OSError:
        try:
            if os.path.exists(temporary_path) and not os.path.exists(legacy_entry.path):
                os.rename(temporary_path, legacy_entry.path)
        except OSError:
            pass
    return desired_path



def platform_config_locations():
    """Return independent RiqatonyPad preference paths (clean identity cutover)."""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA") or os.path.join(
            os.path.expanduser("~"), "AppData", "Roaming"
        )
        return os.path.join(appdata, "brunonlinespace", "RiqatonyPad"), ()

    config_home = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(config_home, "brunonlinespace", "riqatonypad"), ()



def configure_platform_identity():
    """Apply a stable Windows shell identity while remaining cross-platform."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "brunonlinespace.RiqatonyPad"
        )
    except (AttributeError, OSError):
        pass



def appimage_theme_resources():
    """Return RiqatonyPad's bundled theme-resource locations.

    The historical helper name and packaged QSS resources are retained for
    preference/backward compatibility and AppImage availability detection.
    Dark chrome retains RiqatonyPad's existing palette-only model; Light
    chrome follows the canonical Rico Plus light palette in both Portable/source
    and AppImage runtimes.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = []
    appdir = os.environ.get("APPDIR")
    if appdir:
        candidates.append(os.path.join(appdir, "usr", "share", "riqatonypad", "styles"))
    candidates.extend((
        os.path.join(script_dir, "styles"),
        os.path.join(script_dir, "assets", "styles"),
        os.path.join(script_dir, "packaging", "appimage", "styles"),
        os.path.normpath(os.path.join(script_dir, "..", "assets", "styles")),
    ))
    for style_directory in candidates:
        resources = {
            "dark": os.path.join(style_directory, "breeze-dark.qss"),
            "light": os.path.join(style_directory, "breeze-light.qss"),
        }
        if all(os.path.isfile(path) for path in resources.values()):
            return resources
    return {}



def main():
    if "--version" in sys.argv[1:]:
        print(f"{APP_NAME} {APP_VERSION}")
        return

    configure_platform_identity()

    app = QApplication(sys.argv)
    app.setProperty(
        "riqatonypad_original_style",
        app.style().objectName(),
    )
    app._riqatonypad_original_palette = QPalette(app.palette())
    original_window_colour = app.palette().color(QPalette.ColorRole.Window)
    app.setProperty(
        "riqatonypad_original_icon_variant",
        "dark" if original_window_colour.lightness() < 128 else "light",
    )
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("brunonlinespace")
    if sys.platform != "win32":
        app.setDesktopFileName("riqatonypad")

    icon_path = resource_path("icons", "riqatonypad.png")
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # QApplication removes Qt-specific options from its argument list. Every
    # remaining regular file is opened, matching the desktop entry's %F field.
    file_arguments = [
        os.path.abspath(argument)
        for argument in app.arguments()[1:]
        if os.path.isfile(argument)
    ]

    window = RiqatonyPad(file_arguments[0] if file_arguments else None)

    if FORMAT_PARITY_PROBE_MODE:
        # Run synchronously: the parity gate validates document semantics, not
        # an off-screen platform plugin's ability to propagate top-level size
        # hints. This avoids timer/event-loop deadlocks while still exercising
        # the real RiqatonyPad editor commands and serializer in each runtime.
        import hashlib
        editor=window.visual_editor; editor.clear(); window.file_path=None
        editor.document().setDefaultFont(QFont("Sans Serif",11)); editor.document().setDocumentMargin(4.0)
        cursor=editor.textCursor(); cursor.insertText("Alpha"); cursor.insertBlock(); cursor.insertText("Beta"); cursor.insertBlock(); cursor.insertText("Gamma")
        # With no selection, character formatting should understand the word
        # under the caret rather than changing only future typing.
        word_probe=QTextCursor(editor.document()); word_probe.setPosition(2); editor.setTextCursor(word_probe); window.toggle_italic()
        word_ok=True
        for position in range(5):
            q=QTextCursor(editor.document()); q.setPosition(position)
            if not q.charFormat().fontItalic(): word_ok=False; break
        beta_probe=QTextCursor(editor.document()); beta_probe.setPosition(editor.document().findBlockByNumber(1).position())
        word_ok=word_ok and not beta_probe.charFormat().fontItalic()
        # Partial selection must style the whole first paragraph immediately.
        probe=QTextCursor(editor.document()); probe.setPosition(0); probe.setPosition(3,QTextCursor.MoveMode.KeepAnchor); editor.setTextCursor(probe); window.apply_heading(2)
        # Two selected paragraphs must become one coherent bullet list.
        second=editor.document().findBlockByNumber(1); third=editor.document().findBlockByNumber(2); probe=QTextCursor(editor.document()); probe.setPosition(second.position()); probe.setPosition(third.position()+max(0,third.length()-1),QTextCursor.MoveMode.KeepAnchor); editor.setTextCursor(probe); window.toggle_bullet_list()
        second_object=second.blockFormat().objectIndex(); third_object=third.blockFormat().objectIndex()
        list_ok=(second.textList() is not None and third.textList() is not None and second_object>=0 and second_object==third_object and second.blockFormat().leftMargin()==third.blockFormat().leftMargin() and second.blockFormat().textIndent()==third.blockFormat().textIndent())
        first_check=QTextCursor(editor.document()); first_check.setPosition(0); first_check.setPosition(1,QTextCursor.MoveMode.KeepAnchor); style_size=float(first_check.charFormat().fontPointSize() or 0.0); style_ok=abs(style_size-20.0)<0.01
        # Clear Formatting must remove paragraph/list styling but preserve a link.
        link_cursor=QTextCursor(editor.document()); link_cursor.setPosition(second.position()); link_cursor.setPosition(second.position()+4,QTextCursor.MoveMode.KeepAnchor); link_fmt=QTextCharFormat(); link_fmt.setAnchor(True); link_fmt.setAnchorHref("https://example.invalid/"); link_fmt.setFontWeight(QFont.Weight.Bold); link_cursor.mergeCharFormat(link_fmt); editor.setTextCursor(link_cursor); window.clear_formatting(); link_after=QTextCursor(editor.document()); link_after.setPosition(second.position()); link_after.setPosition(second.position()+4,QTextCursor.MoveMode.KeepAnchor); link_ok=link_after.charFormat().isAnchor() and link_after.charFormat().anchorHref()=="https://example.invalid/"
        # Paragraph-only operations must not clone the first block's list or
        # alignment onto the rest of a mixed selection.  This specifically
        # guards the 0.7.1 regression where Line Spacing could create bullets
        # across unrelated text or reset centred/right paragraphs to Left.
        editor.clear(); cursor=editor.textCursor(); cursor.insertText("Left"); cursor.insertBlock(); cursor.insertText("Right"); second=cursor.block(); right_fmt=QTextBlockFormat(second.blockFormat()); right_fmt.setAlignment(Qt.AlignmentFlag.AlignRight); cursor.setBlockFormat(right_fmt); cursor.insertBlock(); cursor.insertText("Listed"); third=cursor.block(); list_fmt=QTextListFormat(); list_fmt.setStyle(QTextListFormat.Style.ListDisc); list_fmt.setIndent(1); cursor.createList(list_fmt)
        first=editor.document().findBlockByNumber(0); second=editor.document().findBlockByNumber(1); third=editor.document().findBlockByNumber(2)
        mixed=QTextCursor(editor.document()); mixed.setPosition(first.position()); mixed.setPosition(third.position()+max(0,third.length()-1),QTextCursor.MoveMode.KeepAnchor); editor.setTextCursor(mixed); window.set_line_spacing(150)
        blocks=(first,second,third)
        spacing_ok=all(abs(float(block.blockFormat().lineHeight() or 0)-150.0)<0.01 and int(block.blockFormat().lineHeightType())==int(QTextBlockFormat.LineHeightTypes.ProportionalHeight.value) for block in blocks)
        paragraph_scope_ok=(not (first.blockFormat().alignment() & Qt.AlignmentFlag.AlignRight) and bool(second.blockFormat().alignment() & Qt.AlignmentFlag.AlignRight) and first.textList() is None and second.textList() is None and third.textList() is not None)
        payload=window._document_payload("rtf"); digest=hashlib.sha256(payload).hexdigest()
        if not (word_ok and style_ok and list_ok and link_ok and spacing_ok and paragraph_scope_ok):
            print(f"FORMAT_PARITY_SEMANTIC_FAILURE word={int(word_ok)} style={int(style_ok)} list={int(list_ok)} link={int(link_ok)} spacing={int(spacing_ok)} scope={int(paragraph_scope_ok)}",flush=True)
            raise SystemExit(3)
        print(f"FORMAT_PARITY {digest} word=1 style=1 list=1 link=1 clear=1 spacing=1 scope=1 margin={editor.document().documentMargin():g} frame={editor.frameShape().value} contents={editor.contentsMargins().left()},{editor.contentsMargins().top()},{editor.contentsMargins().right()},{editor.contentsMargins().bottom()}",flush=True)
        return

    window.show()
    for file_path in file_arguments[1:]:
        window.new_window(file_path)

    if SMOKE_TEST_MODE:
        # Deterministic packaging smoke test: construct the complete UI, enter
        # the event loop once, validate the active packaged theme when AppImage
        # resources are present, explicitly destroy every test window, emit a
        # machine-checkable marker, then exit without touching preferences.
        #
        # Do not let Qt's implicit last-window policy race the explicit teardown.
        # AppDir/offscreen Qt can otherwise finish every assertion and print the
        # PASS marker yet remain alive until the builder's timeout kills it.
        app.setQuitOnLastWindowClosed(False)

        def finish_smoke_test():
            # View -> Show Status must describe the actual visible status bar at
            # startup; a prior regression restored visibility but not QAction state.
            if window.status_bar_action.isChecked() != window.app_status_bar.isVisible():
                print("GUI smoke test failed: Show Status action is not synchronized with status-bar visibility.",flush=True); app.exit(2); return
            # Repeated Help-dialog lifecycle regression: these used to crash in
            # both Portable and AppImage because the required Qt widget classes
            # were not imported and the dialogs used local nested exec() loops.
            for opener, attribute in ((window.show_tutorial_wizard, "tutorial_dialog"), (window.show_keyboard_shortcuts_dialog, "shortcuts_dialog")):
                opener(); app.processEvents()
                dialog=getattr(window,attribute,None)
                if dialog is None or not dialog.isVisible():
                    print(f"GUI smoke test failed: {attribute} did not open.",flush=True); app.exit(2); return
                dialog.close(); app.processEvents()
                opener(); app.processEvents()
                dialog=getattr(window,attribute,None)
                if dialog is None or not dialog.isVisible():
                    print(f"GUI smoke test failed: {attribute} did not reopen.",flush=True); app.exit(2); return
                dialog.close(); app.processEvents()
            before_windows=set(OPEN_WINDOWS)
            if not window.open_documentation():
                print("GUI smoke test failed: bundled RTF documentation did not open.",flush=True); app.exit(2); return
            app.processEvents()
            docs=[item for item in OPEN_WINDOWS if item not in before_windows]
            if len(docs)!=1 or not docs[0].file_path or not docs[0].file_path.endswith("RiqatonyPad-Documentation.rtf") or not docs[0].view_only:
                print("GUI smoke test failed: documentation window contract mismatch.",flush=True); app.exit(2); return
            docs[0]._skip_close_save_prompt=True; docs[0].close(); app.processEvents()
            if window.appimage_theme_available:
                requested=os.environ.get("RIQATONYPAD_APPIMAGE_THEME","").strip().lower()
                expected_theme=requested if requested in ("system","dark","light") else window.effective_appimage_theme()
                actual_theme=window.effective_appimage_theme()
                if actual_theme != expected_theme:
                    print(f"GUI smoke test failed: expected RiqatonyPad theme {expected_theme}, got {actual_theme}.",flush=True); app.exit(2); return
                if app.styleSheet().strip():
                    print("GUI smoke test failed: Markopad-style themes must not install application QSS in any runtime.",flush=True); app.exit(2); return
                if expected_theme in ("dark","light"):
                    expected_window="#202326" if expected_theme=="dark" else "#d4d4d4"
                    actual_window=app.palette().color(QPalette.ColorRole.Window).name().lower()
                    if actual_window != expected_window:
                        print(f"GUI smoke test failed: {expected_theme} palette window is {actual_window}, expected {expected_window}.",flush=True); app.exit(2); return
                requested_icons=os.environ.get("RIQATONYPAD_APPIMAGE_ICONSET","").strip().lower()
                expected_icons=requested_icons if requested_icons in ("new","classic","original") else window.effective_appimage_icon_set()
                actual_icons=window.effective_appimage_icon_set()
                if actual_icons != expected_icons or window.custom_icon("save").isNull():
                    print(f"GUI smoke test failed: expected RiqatonyPad icon set {expected_icons}, got {actual_icons}.",flush=True); app.exit(2); return
                window._refresh_interface_geometry(); app.processEvents()
                bad_ribbon=[(button.width(),button.height()) for button in window.ribbon_buttons if button.size()!=QSize(RIBBON_BUTTON_SIZE,RIBBON_BUTTON_SIZE)]
                expected_ribbon_selectors=((window.font_combo,RIBBON_FONT_FAMILY_WIDTH),(window.font_size_combo,RIBBON_BUTTON_SIZE),(window.heading_combo,RIBBON_BUTTON_SIZE),(window.line_spacing_combo,RIBBON_BUTTON_SIZE))
                bad_ribbon_selectors=[(widget.toolTip(),widget.width(),widget.height()) for widget,width in expected_ribbon_selectors if widget.size()!=QSize(width,RIBBON_BUTTON_SIZE)]
                if bad_ribbon or bad_ribbon_selectors or window.ribbon_tabs.height()<window._ribbon_expanded_minimum_height:
                    print(f"GUI smoke test failed: Ribbon 52px geometry mismatch: {bad_ribbon[:4]} {bad_ribbon_selectors}.",flush=True); app.exit(2); return
                previous_interface=window.interface_style; window.set_interface_style("retro",persist=False); window._refresh_interface_geometry(); app.processEvents()
                bad_retro=[]
                for widget in window.retro_toolbar_widgets:
                    width=RIBBON_FONT_FAMILY_WIDTH if isinstance(widget,QFontComboBox) else RIBBON_BUTTON_SIZE
                    if widget.size()!=QSize(width,RIBBON_BUTTON_SIZE): bad_retro.append((widget.toolTip(),widget.width(),widget.height()))
                extension=window.retro_toolbar.findChild(QToolButton,"qt_toolbar_ext_button")
                scroll_bad=(extension is not None or not isinstance(window.retro_toolbar,RibbonScrollArea) or window.retro_toolbar_body.height()<RIBBON_BUTTON_SIZE)
                if bad_retro or scroll_bad:
                    print(f"GUI smoke test failed: Retro scroll/52px geometry mismatch: {bad_retro[:4]} overflow_button={extension is not None}.",flush=True); app.exit(2); return
                window.set_interface_style(previous_interface,persist=False); window._refresh_interface_geometry(); app.processEvents()
                success_message=f"GUI smoke test passed. Theme: {expected_theme}. Icons: {expected_icons}. Ribbon/Retro geometry: 52px grid."
            else:
                success_message="GUI smoke test passed. Theme: portable/system resources."

            # Clean shutdown is part of the smoke contract.  Close the retained
            # modeless dialogs and every RiqatonyPad top-level window, force Qt's
            # DeferredDelete events through, and only then report success.  This
            # keeps the probe honest: the builder never treats a timed-out process
            # as success merely because a PASS line appeared in its output.
            for candidate in tuple(OPEN_WINDOWS):
                candidate._skip_close_save_prompt=True
                for attribute in ("tutorial_dialog","shortcuts_dialog","about_dialog","new_document_defaults_dialog","replace_dialog"):
                    dialog=getattr(candidate,attribute,None)
                    if dialog is not None:
                        dialog.close(); dialog.deleteLater(); setattr(candidate,attribute,None)
                candidate.close()
            app.processEvents()
            QApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
            app.processEvents()
            if OPEN_WINDOWS:
                print(f"GUI smoke test failed: clean shutdown left {len(OPEN_WINDOWS)} RiqatonyPad window(s) registered.",flush=True)
                app.exit(2); return
            print(success_message,flush=True)
            app.exit(0)

        QTimer.singleShot(0, finish_smoke_test)

    sys.exit(app.exec())

