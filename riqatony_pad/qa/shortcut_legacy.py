#!/usr/bin/env python3
"""Read original pure shortcut-helper prefix for historical regression fingerprints."""
from pathlib import Path


def legacy_read_bytes(root: Path, rel: str) -> bytes:
    if rel != 'widgets/shortcut_search.py':
        return (root/rel).read_bytes()
    source = (root/'widgets/keyboard_shortcuts.py').read_bytes()
    length = int((root/'qa/x125-helper-length.txt').read_text())
    assert len(source) > length, 'dialog method was not appended'
    return source[:length]
