# Shared Pad status-message presentation conventions.
# SPDX-License-Identifier: GPL-3.0-or-later
"""The agreed four-second, sentence and unresolved-warning contract."""

DEFAULT_MESSAGE_DURATION_MS = 4000

def status_sentence(message: str) -> str:
    text = str(message).strip()
    if not text:
        return text
    if text.endswith(("…", "...")):
        return text.rstrip(". …") + "."
    return text if text.endswith(".") else text + "."

def is_critical_status(message: str) -> bool:
    return str(message).startswith((
        "Could not load ", "Could not save ",
        "Backing file missing;", "File changed outside ",
        "RTF opened with compatibility warnings.",
    ))
