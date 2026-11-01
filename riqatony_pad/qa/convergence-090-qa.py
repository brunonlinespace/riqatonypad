#!/usr/bin/env python3
"""Dependency-free inherited RiqatonyPad 0.9.0 convergence/Help regression gate."""

from __future__ import annotations

import ast
from pathlib import Path
import sys

from source_contract import contract_text
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rtf_new_document import NewDocumentDefaults, build_new_document_rtf_payload
from widgets.keyboard_shortcuts import shortcut_query_matches, shortcut_tokens


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


# Exact Rico Plus fuzzy-shortcut semantics: token aliases, reordered modifiers,
# optional plus signs and partial modifier queries.
tokens = shortcut_tokens("Ctrl+Alt+Shift+P")
require(shortcut_query_matches("shift ctrl p", tokens), "reordered modifiers failed")
require(shortcut_query_matches("ctl p", tokens), "Ctl alias failed")
require(shortcut_query_matches("control+alt+p", tokens), "Control alias/plus form failed")
require(shortcut_query_matches("alt shift", tokens), "partial modifier query failed")
require(not shortcut_query_matches("meta p", tokens), "unassigned modifier falsely matched")
require(not shortcut_query_matches("", tokens), "empty shortcut query must not match")


# Prior RiqatonyPad 0.8.9 builder, preserved here only as a byte-for-byte regression
# oracle for the extraction into the shared pure document-domain builder.
def legacy_payload(defaults: NewDocumentDefaults) -> bytes:
    family=(defaults.font_family or "Sans Serif").strip() or "Sans Serif"
    safe_family=family.replace("\\"," ").replace("{"," ").replace("}"," ").replace(";"," ").strip() or "Sans Serif"
    escaped=[]
    for char in safe_family:
        code=ord(char)
        if 32 <= code < 127:
            escaped.append(char)
        else:
            encoded=char.encode("utf-16-le",errors="replace")
            for offset in range(0,len(encoded),2):
                unit=int.from_bytes(encoded[offset:offset+2],"little")
                escaped.append(f"\\u{unit if unit < 32768 else unit-65536}?")
    align={"left":"\\ql","centre":"\\qc","right":"\\qr","justify":"\\qj"}.get(defaults.alignment,"\\ql")
    spacing=max(50,min(400,int(defaults.line_spacing)))
    point_size=max(6,min(72,int(defaults.font_size)))
    char_controls=f"\\f0\\fs{point_size*2}"
    if defaults.font_weight=="bold": char_controls+="\\b"
    if defaults.font_slant=="italic": char_controls+="\\i"
    sl=round(spacing*2.4)
    body=(
        "{\\rtf1\\ansi\\ansicpg1252\\deff0\\uc1"
        "{\\fonttbl{\\f0\\fnil "+"".join(escaped)+";}}"
        "{\\colortbl ;}"
        +char_controls+"\\viewkind4\\widowctrl\n"
        "\\pard"+align+"\\li0\\ri0\\fi0\\sb0\\sa0"
        +f"\\sl{sl}\\slmult1"
        +"{\\plain"+char_controls+" }\\par\n}"
    )
    return body.encode("ascii",errors="strict")

cases = (
    NewDocumentDefaults(),
    NewDocumentDefaults("Liberation Serif", 18, "bold", "italic", 150, "centre"),
    NewDocumentDefaults("Noto Sans Ω", 6, "normal", "roman", 50, "right"),
    NewDocumentDefaults("A;B{C}\\D", 72, "bold", "roman", 400, "justify"),
    NewDocumentDefaults("Emoji 😀", 500, "normal", "italic", 999, "unknown"),
)
for case in cases:
    require(build_new_document_rtf_payload(case) == legacy_payload(case), f"new-document payload drift: {case!r}")

source = contract_text(ROOT)
tree = ast.parse(source)
cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RiqatonyPad")
methods = {node.name: node for node in cls.body if isinstance(node, ast.FunctionDef)}

prefs_source=(ROOT/'widgets/rwpyn/editor_preferences.py').read_text(encoding='utf-8')
prefs_cls=next(n for n in ast.parse(prefs_source).body if isinstance(n,ast.ClassDef) and n.name=='EditorPreferencesMixin')
prefs_methods={n.name:n for n in prefs_cls.body if isinstance(n,ast.FunctionDef)}
def segment(name: str) -> str:
    if name in prefs_methods:return ast.get_source_segment(prefs_source,prefs_methods[name]) or ""
    return ast.get_source_segment(source, methods[name]) or ""

builder = segment("_build_new_document_template_payload")
require("build_new_document_rtf_payload" in builder and "NewDocumentDefaults" in builder, "RiqatonyPad builder is not the shared adapter")
require("utf-16-le" not in builder and "char_controls" not in builder, "legacy inline RTF builder still present in RiqatonyPad method")

shortcuts = segment("show_keyboard_shortcuts_dialog")
for needle in (
    "shortcut_tokens(shortcut)",
    "shortcut_query_matches(query,shortcut_search)",
    'QLabel("No matching shortcuts.",dialog)',
    'setPlaceholderText("Search commands or shortcuts")',
    'setAccessibleName("Search keyboard shortcuts")',
    'QLabel("Menu:",dialog)',
):
    require(needle in shortcuts, f"shortcut-search port missing: {needle}")

about = segment("show_about_dialog")
for needle in (
    "https://github.com/59de44955ebd/PyWordpad",
    "Microsoft WordPad-inspired document features",
    "<b>Configuration:</b>",
    'QColor("#0068A6")',
    "QPalette.ColorRole.LinkVisited",
    'replace("/", "/&#8203;")',
):
    require(needle in about, f"About cleanup missing: {needle}")
require("PyWordpad</a> " in about and "PyWordpad licensed" not in about and "PyWordpad license" not in about, "About must attribute PyWordpad without a licensing claim")

tour = segment("show_tutorial_wizard")
for needle in (
    "View → Editor Toolbar",
    "Configure → Editor Settings",
    "same shared command registry",
    "full applicable command/selector inventory",
    "fuzzy shortcut matching",
):
    require(needle in tour, f"Tutorial cleanup missing: {needle}")
require("Settings → Toolbar" not in tour, "stale Tutorial toolbar path remains")

help_rtf = (ROOT / "docs" / "RiqatonyPad-Documentation.rtf").read_text(encoding="utf-8")
for needle in (
    "View > Editor Miscellaneous > New Document Defaults",
    "same shared command registry",
    "reordered modifiers",
    "PyWordpad",
    "Microsoft WordPad-inspired",
    "RiqatonyPad 1.1.2",
):
    require(needle in help_rtf, f"bundled Help cleanup missing: {needle}")
require("View > More Settings > New Document Defaults" not in help_rtf, "stale Help path remains")

release_notes = (ROOT / "docs" / "RELEASE_NOTES.md").read_text(encoding="utf-8")
require("No RTF codec/serializer" in release_notes, "current release must document retained RTF baseline")

print("PASS: inherited 0.9.0 fuzzy search, shared new-document builder and About/Tour/Help cleanup")
