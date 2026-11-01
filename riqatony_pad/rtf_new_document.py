#!/usr/bin/env python3
# Ricopad
# Copyright (C) 2026 Bruno Machado
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure new-document defaults and RTF payload generation.

Ported from Rico Plus 0.0.4-r8's Ricopad-derived document-domain builder so
standalone Ricopad and Rico Plus share one definition of a blank RTF payload.
This module deliberately has no Qt dependency.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NewDocumentDefaults:
    font_family: str = "Sans Serif"
    font_size: int = 12
    font_weight: str = "normal"
    font_slant: str = "roman"
    line_spacing: int = 115
    alignment: str = "left"


def build_new_document_rtf_payload(defaults: NewDocumentDefaults) -> bytes:
    """Build the interoperable blank RTF used by Ricopad new-document semantics."""
    family = (defaults.font_family or "Sans Serif").strip() or "Sans Serif"
    safe_family = (
        family.replace("\\", " ")
        .replace("{", " ")
        .replace("}", " ")
        .replace(";", " ")
        .strip()
        or "Sans Serif"
    )
    escaped: list[str] = []
    for char in safe_family:
        code = ord(char)
        if 32 <= code < 127:
            escaped.append(char)
        else:
            encoded = char.encode("utf-16-le", errors="replace")
            for offset in range(0, len(encoded), 2):
                unit = int.from_bytes(encoded[offset:offset + 2], "little")
                escaped.append(f"\\u{unit if unit < 32768 else unit - 65536}?")

    align = {
        "left": "\\ql",
        "centre": "\\qc",
        "right": "\\qr",
        "justify": "\\qj",
    }.get(defaults.alignment, "\\ql")
    spacing = max(50, min(400, int(defaults.line_spacing)))
    point_size = max(6, min(72, int(defaults.font_size)))
    char_controls = f"\\f0\\fs{point_size * 2}"
    if defaults.font_weight == "bold":
        char_controls += "\\b"
    if defaults.font_slant == "italic":
        char_controls += "\\i"

    # 240 twips is one proportional line in RTF; Ricopad stores percent.
    sl = round(spacing * 2.4)
    body = (
        "{\\rtf1\\ansi\\ansicpg1252\\deff0\\uc1"
        "{\\fonttbl{\\f0\\fnil " + "".join(escaped) + ";}}"
        "{\\colortbl ;}"
        + char_controls + "\\viewkind4\\widowctrl\n"
        "\\pard" + align + "\\li0\\ri0\\fi0\\sb0\\sa0"
        + f"\\sl{sl}\\slmult1"
        + "{\\plain" + char_controls + " }\\par\n}"
    )
    return body.encode("ascii", errors="strict")
