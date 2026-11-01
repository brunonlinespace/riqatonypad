# Licensing and provenance

Ricopad is distributed under GPLv3-or-later.

## Code inputs reviewed

- Nuxpad 2.0.0-rc5.1 — reviewed as the printing/pagination reference for `QPrinter.ScreenResolution`, paint-device-aligned QTextDocument layout, and shared printer/PDF pagination. Ricopad intentionally does not copy Nuxpad's plain-text-only forced-black print formatting because RTF colours are document content.
- PyWordpad snapshot — behavioural reference only; its Win32/ctypes code was not copied because no explicit licence file was present in the supplied snapshot.

## Icon families

Ricopad 0.8.5 uses the three canonical Rico command-icon families ported byte-for-byte from Rico Plus 0.0.4-r8:

- **Riqa Icons Harmony** (`new`) — default family in RiqatonyPad 2.0.0-x16.2.
- **Riqa Icons Humility** (`classic`).
- **Riqa Icons Heritage** (`original`).

The three active families were re-patched in x16.1 with the user's supplied light/dark 144-icon-per-variant PNG packs. Older asset names not present in those packs are retained from the x16.0 source to preserve existing command references; new supplied asset names are added. Family names and on-screen selectors now use Riqa Icons Harmony, Riqa Icons Humility and Riqa Icons Heritage. Technical preference keys and the default Harmony family remain unchanged. Historical imports and the earlier x16.0 Harmony refresh are documented in the preserved release history.

Previously removed SVG icon generation tools are not part of the current source; Harmony, Classic and Legacy ship pre-rendered PNGs only. The Ricopad application/logo icon is unchanged.

Qt/PyQt6 and PyInstaller remain governed by their own licences. The application packages pre-rendered PNG icons only; former SVG generation tools and SVG assets were retired in 2.0.0-x13.5.
