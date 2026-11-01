#!/usr/bin/env python3
"""Qt runtime regression tests for RiqatonyPad 0.8.5 highlight clearing."""
from __future__ import annotations

import os
import pathlib
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QA_STATE = tempfile.TemporaryDirectory(prefix="riqatonypad-highlight-qa-")
os.environ["XDG_CONFIG_HOME"] = QA_STATE.name
sys.dont_write_bytecode = True
# Suppress first-run tutorial before importing app.py (the module consumes
# this private switch before QApplication sees argv).
sys.argv.append("--riqatonypad-smoke-test")

PACKAGE = pathlib.Path(__file__).resolve().parents[1]
CORPUS = pathlib.Path(__file__).resolve().parent / "highlight-corpus"
sys.path.insert(0, str(PACKAGE))
# Retain the outer source root so lazy riqatony_pad.widgets imports resolve,
# matching the main.py Portable launcher while Qt QA runs as a standalone script.
sys.path.insert(0, str(PACKAGE.parent))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QApplication

import app as riqatonypad_module
from app import RiqatonyPad
from rtf_codec import (
    RTF_AUTOMATIC_CONTRAST_PROPERTY,
    _qt_brush_colour,
    _rtf_clear_automatic_foreground,
    decode_rtf,
    document_to_rtf,
    populate_qtextdocument_from_rtf_model,
)

riqatonypad_module.platform_config_locations = lambda: (QA_STATE.name, ())
app = QApplication.instance() or QApplication(["riqatonypad-highlight-qa"])


def require(value, message):
    if not value:
        raise AssertionError(message)


def surface():
    window = RiqatonyPad()
    return window, window.visual_editor


def close_surface(window):
    # These windows contain deliberately modified in-memory documents.  A normal
    # close would invoke RiqatonyPad's user-facing unsaved-changes QMessageBox; under
    # QT_QPA_PLATFORM=offscreen that modal dialog is invisible and blocks build QA.
    # Use the application's existing controlled-close bypass rather than changing
    # production close/save behavior or weakening the formatting assertions.
    window._skip_close_save_prompt = True
    window.close()


def set_selection(editor, start, end):
    cursor = QTextCursor(editor.document())
    cursor.setPosition(start)
    cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
    editor.setTextCursor(cursor)


def format_at(window, position):
    # Keep the complete QTextCharFormat in Qt rather than materialising its
    # QVariant property map in Python. Some Qt/PyQt6 builds expose opaque font
    # properties (for example QMap<QFont::Tag,uint>) that cannot be converted
    # to Python objects by QTextFormat.properties(). QTextCharFormat's native
    # equality still compares the complete format, so this remains an exact
    # before/after regression check without discarding unsupported properties.
    return QTextCharFormat(
        window._character_format_at_position(window.visual_editor.document(), position)
    )


def round_trip_selection(text, start, end, colour):
    window, editor = surface()
    editor.setPlainText(text)
    before = [format_at(window, i) for i in range(start, end)]
    set_selection(editor, start, end)
    window._apply_highlight(colour=QColor(colour))
    for i in range(start, end):
        fmt = window._character_format_at_position(editor.document(), i)
        require(_qt_brush_colour(fmt.background()) is not None, f"highlight missing at {i}")
        require(bool(fmt.property(RTF_AUTOMATIC_CONTRAST_PROPERTY)), f"automatic contrast tag missing at {i}")
    window.clear_highlight()
    after = [format_at(window, i) for i in range(start, end)]
    require(after == before, f"clear highlight did not restore exact character formatting for {text[start:end]!r}")
    payload = document_to_rtf(editor.document())
    require(br"\\highlight" not in payload, "cleared highlight serialized back into RTF")
    return window


# First/middle/final selection boundaries all return to their original exact format.
for text, start, end in (
    ("first middle final", 0, 5),
    ("first middle final", 6, 12),
    ("first middle final", 13, 18),
):
    w = round_trip_selection(text, start, end, "#fff200")
    close_surface(w)

# Dark highlight uses automatic white contrast; clearing must remove it completely.
w = round_trip_selection("before fixing after", 7, 13, "#000000")
for i in range(7, 13):
    fmt = w._character_format_at_position(w.visual_editor.document(), i)
    require(_qt_brush_colour(fmt.foreground()) is None, "automatic white foreground survived black-highlight clearing")
    require(not fmt.hasProperty(RTF_AUTOMATIC_CONTRAST_PROPERTY), "automatic contrast marker survived clearing")
close_surface(w)

# An explicit user foreground is never mistaken for RiqatonyPad's automatic contrast.
w, editor = surface(); editor.setPlainText("before fixing after")
set_selection(editor, 7, 13)
explicit = QTextCharFormat(); explicit.setForeground(QColor("#d00000")); explicit.setProperty(RTF_AUTOMATIC_CONTRAST_PROPERTY, False)
editor.textCursor().mergeCharFormat(explicit)
before = [format_at(w, i) for i in range(7, 13)]
set_selection(editor, 7, 13); w._apply_highlight(colour=QColor("#fff200"))
for i in range(7, 13):
    fmt = w._character_format_at_position(editor.document(), i)
    require(_qt_brush_colour(fmt.foreground()).name().lower() == "#d00000", "explicit foreground was replaced by highlight contrast")
    require(not bool(fmt.property(RTF_AUTOMATIC_CONTRAST_PROPERTY)), "explicit foreground was tagged automatic")
w.clear_highlight()
require([format_at(w, i) for i in range(7, 13)] == before, "explicit foreground did not survive highlight/clear exactly")
close_surface(w)

# Caret-only clear uses WordUnderCursor and must clean the whole touched word.
w, editor = surface(); editor.setPlainText("before fixing after")
set_selection(editor, 7, 13); w._apply_highlight(colour=QColor("#fff200"))
caret = QTextCursor(editor.document()); caret.setPosition(9); editor.setTextCursor(caret); w.clear_highlight()
for i in range(7, 13):
    fmt = w._character_format_at_position(editor.document(), i)
    require(_qt_brush_colour(fmt.background()) is None, "caret clear left highlight inside the word")
    require(_qt_brush_colour(fmt.foreground()) is None, "caret clear left automatic contrast inside the word")
    require(not fmt.hasProperty(RTF_AUTOMATIC_CONTRAST_PROPERTY), "caret clear left automatic marker inside the word")
close_surface(w)

# Reproduce the exact supplied regression sample from exp6, clear only `fixing`,
# and verify it rejoins the surrounding ordinary run semantically.
w, editor = surface()
decoded = decode_rtf((CORPUS / "highlighted.rtf").read_bytes())
if not populate_qtextdocument_from_rtf_model(editor.document(), decoded.model):
    editor.document().setHtml(decoded.html)
    if decoded.automatic_foreground:
        _rtf_clear_automatic_foreground(editor.document(), decoded.automatic_foreground)
plain = editor.toPlainText(); start = plain.index("fixing"); end = start + len("fixing")
set_selection(editor, start, end); w.clear_highlight()
reference = format_at(w, start - 1)
for i in range(start, end):
    require(format_at(w, i) == reference, f"supplied corpus clear left a different format at fixing[{i-start}]")
payload = document_to_rtf(editor.document())
require(br"\\highlight" not in payload, "supplied highlighted sample still serializes highlight after clear")
require(br"\\red255\\green242\\blue0;" not in payload, "unused supplied yellow highlight colour survived serialization")
require(br"{\\plain\\f0\\fs24 f}{\\plain\\f0\\fs24 ixing}" not in payload, "supplied regression still serializes the f/ixing split")
close_surface(w)

print("highlight-runtime-qa: PASS")
