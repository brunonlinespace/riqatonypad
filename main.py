#!/usr/bin/env python3
"""Location-independent portable RiqatonyPad source launcher."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    program_dir = root / "riqatony_pad"
    entry_point = program_dir / "app.py"

    if not entry_point.is_file():
        raise SystemExit(
            "RiqatonyPad's program folder is incomplete: "
            f"{entry_point} was not found. Keep main.py beside the riqatony_pad folder."
        )

    sys.path.insert(0, str(program_dir))
    runpy.run_path(str(entry_point), run_name="__main__")


if __name__ == "__main__":
    main()
