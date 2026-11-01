## RiqatonyPad 2.0.0 — Final version promotion (2026-11-01)

Promote the existing 2.0.0-x16.9 source baseline to final **2.0.0** without introducing editor functionality, RTF codec, icon-artwork, file-safety or build-workflow changes. Update the source application version, Suite component identity, AppImage and Windows packaging versions, and release QA version assertions. The GitHub-root README changes only its approved current-release field; its pinned independent authority remains intact.

All changes in the x16.9 Find/Replace toggle release and preceding x16.8 Qt regression-import and x16.7 Fedora builder corrections are retained. Promotion alone does **not** certify successful native Fedora AppImage building, real KDE/Qt interactions or production acceptance; those must be verified on the target host.

## RiqatonyPad 2.0.0-x16.9 — Reliable Find/Replace command toggling

The Find and Find/Replace commands now treat a repeated request for the currently displayed search mode as a toggle, even when clicking the Ribbon/Retro command moves focus away from the search field. Switching between Find and Find/Replace continues to focus the requested input. Both editor layouts and transient search behavior are preserved. The old search method depended entirely on the target QLineEdit retaining focus, which was not a reliable indicator of a repeated mouse click. No document content or file handling changes.

The protected GitHub README and its independently pinned authority remain unchanged except for the permitted current-release field. The user clarified that the separate request to remove README lines 2 and 3 concerns Riqatony Desk, not this Pad release.

Static and dependency-free behavior regressions can run without PyQt6; actual Fedora KDE mouse/keyboard behavior remains to be verified on the target platform. Comparison found the same focus-dependent toggle in Riqatony Desk, plus embedded editor commands that use show-only, but **Riqatony Desk is not changed in this Pad release**.

## RiqatonyPad 2.0.0-x16.8 — Qt regression QA import-path hotfix

The build failure after `delete-line-runtime-qa: PASS` was caused by two active PyQt6 tests that still imported the removed `riqatonypad.py` module. `highlight-runtime-qa.py` and `qt-rtf-qa.py` now import the current `app.py` host without altering their test assertions. The Fedora builder runs both runtime regression suites inside its isolated PyQt6 virtual environment. A new static import-contract gate rejects references to the deleted host module even when the release environment has no PyQt6. The 2.0.0-x16.7 builder staging fixes are retained unchanged. Native Fedora end-to-end AppImage acceptance remains outstanding.

## RiqatonyPad 2.0.0-x16.7 — Fedora builder correction

The Fedora AppImage builder no longer assumes fifteen top-level Python modules or an obsolete `tools/` directory. The real PyInstaller source-stage now contains every current application Python module and its two import paths, including `widgets.rwpyn.character_count` and `riqatony_pad.widgets.message_conventions`. A new release-gated QA check executes the builder preflight and staging functions, verifies import resolution, and checks negative missing-module cases. Editor code and UI assets are unchanged. A complete Fedora AppImage build is required for final platform acceptance.

# RiqatonyPad 2.0.0-x16.6 — Protected README and Halcyon asset correction (2026-11-01)

- Replace the GitHub README with the user-approved updated copy, changing only current-version metadata. Save the supplied bytes as the independently pinned README authority.
- Rename dark Halcyon `impport-file.png` to `import-file.png` without modifying the PNG contents. Validate that both Halcyon themes contain the exact same 144 filenames.
- Preserve all other icon families, command wiring, configuration and editor functionality.

---

# RiqatonyPad 2.0.0-x16.5 — Halcyon icons and GitHub README protection (2026-11-01)

- Add **Riqa Icons Halcyon** in Settings → App Icons, using `ribbon-icons-aero`, with no icon or toolbar command.
- Preserve the existing three families; restore and protect the root GitHub README with only the current-version update permitted.
- Recover any previous unauthorized README differences under `docs/history/` and add a mandatory version-only release gate.
- No changes to the RTF editor, file workflows or existing icon artwork.

---

## Previous release record — x16.4

# RiqatonyPad 2.0.0-x16.4 — Quick Tour crash correction (2026-11-01)

- Add the missing `QTimer`, `QWizardPage`, `QVBoxLayout` and `QLabel` imports to the extracted `widgets/quick_tour.py`. Without them, opening Quick Tour raises an uncaught Python `NameError`, which PyQt6 may handle as a fatal abort.
- Preserve the existing seven pages, texts, startup checkbox, shortcuts button, callbacks, layout and application behavior.
- Add executable Quick Tour construction/callback regression coverage to the static release gate. The older source-only test did not catch missing imports.
- No changes to RTF editing, icons, toolbar, Word Wrap, file handling or other application code. Live Qt/KDE confirmation remains required.

---

# RiqatonyPad 2.0.0-x16.3 — Pad icon inventory cleanup and command wiring (2026-10-31)

- Remove the 18 old retained PNGs absent from the supplied Harmony, Humility and Heritage icon packs. Each family now has precisely 144 light + 144 dark PNGs. Keep Heritage’s four x16.2 replacement PNGs unchanged.
- Wire `app-drag-and-drop.png` to the App Drag-and-Drop AppMenu parent (independent of radio state).
- Wire `layout.png` to Editor Layout in AppMenu and the Ribbon/Retro shared command inventory.
- Wire `toolbar-tabbed.png` to Ribbon and `toolbar-classic.png` to Retro radio selections in AppMenu and shared toolbar selectors.
- Preserve editor behavior, settings, selection semantics, RTF codec and Word Wrap unchanged. No Desk changes.
- Full static QA is supplied; live KDE/PyQt6 validation remains required.

# RiqatonyPad 2.0.0-x16.2 — Heritage icon corrective patch (2026-10-31)

- Replace only `ribbon-icons-original/{dark,light}/external-editor.png` and `launch-last-file.png` with the four PNGs supplied in `ribbon-icons-original-patch.zip`.
- Harmony and Humility, all other Heritage artwork, editor functionality and existing command wiring remain unchanged.
- Retain x16.1 provenance as historical evidence; x16.2 checks exact replacements and all other icon hashes. Live GUI testing remains outstanding.

# RiqatonyPad 2.0.0-x16.1 — Riqa icon-family re-patch (2026-10-31)

- Install the supplied light/dark PNG artwork for **Riqa Icons Harmony** (`ribbon-icons`), **Riqa Icons Humility** (`ribbon-icons-classic`), and **Riqa Icons Heritage** (`ribbon-icons-original`). Existing asset names absent from the supplied packs are retained for command compatibility. The saved icon-family keys (`new`, `classic`, `original`) and default `new` remain unchanged.
- Align AppMenu, Ribbon/Retro family-selector labels and tooltips; `icons-legacy.png` now identifies the Heritage selector, with the corresponding Harmony/Humility selector icons.
- Re-wire `find.png` to Find; `heading-group.png` to the Paragraph Style AppMenu group; `heading-0.png` through `heading-6.png` to Normal Paragraph/Heading 1–6; and `link-group.png` to the Link AppMenu submenu.
- Re-wire `dirty-duplicate-policy.png` and `dirty-external-policy.png` to their respective unsaved-changes policy submenus.
- **Not in this pass:** `toolbar-tabbed.png` / `toolbar-classic.png` wiring, other mismatched icons, changes to editing, file operations, or toolbar behavior.
- Static source/icon QA only; live Fedora KDE GUI validation is still required.

# RiqatonyPad 2.0.0-x16.0 — Rico Icons Harmony (2026-10-25)

Built strictly from RiqatonyPad 2.0.0-x13.5. Replaced its complete default `assets/ribbon-icons` directory with the user-provided Harmony PNG collection, which matches the family shipped in RiqatonyDesk 1.0.0-x19.0 byte-for-byte. Harmony contains 148 light and 148 dark 64×64 PNGs, including all 106 icon names previously present in each theme and 42 additional names per theme. No SVG assets are present.

Changed the current **Rico Icons Modern** user-facing selection label to **Rico Icons Harmony** (including selected-family feedback). The original preference identifier `new`, default preference and icon loading location remain unchanged; existing saved choices still work. Classic and Legacy assets are preserved byte-for-byte. No changes were made to RTF editing, Unicode Chars, warnings, file lifecycle, application layout or icon loading mechanics.

**Validation:** exact supplied-icon SHA-256 checks, Classic/Legacy predecessor asset checks, required icon coverage, release metadata and scope preservation. Real PyQt6 visual testing requires an installed Qt runtime.

---

# RiqatonyPad 2.0.0-x13.5 — Unicode Chars and PNG-only assets (2026-10-24)

Built solely from 2.0.0-x13.4. The **Chars** indicator now counts extended Unicode grapheme clusters in document text (including spaces, punctuation and one logical separator between paragraphs or table cells). Each inline image/object placeholder counts once. The Qt document is not converted to full plain text per edit: unchanged QTextBlocks retain revision-keyed cached grapheme counts. Cursor-only operations reuse cached counts. Document-size and RTF safety limits remain unchanged.

All **636 SVG files** and the two SVG-dependent icon regeneration scripts were removed. All existing PNG assets remain byte-for-byte identical to x13.4, preserving themes, command icons and the visual interface. Current icon QA checks PNG coverage and checksums. The x13.4 selective backing-warning correction remains unchanged.

**Validation limits:** static and stubbed character-counter tests; Qt/PyQt6 GUI, Unicode boundary integration and large-document performance require host testing.

---

# RiqatonyPad 2.0.0-x13.4 — Backing-warning dismissal precision (2026-10-24)

Built strictly from `2.0.0-x13.3`. The two watcher-issued critical messages for a missing or externally changed backing file now carry explicit backing-warning identity. When the backing state normalizes, only an active warning of that identity is dismissed. An unrelated critical warning (including RTF compatibility or failed load/save) remains visible. Existing message wording, four-second routine timing, message priority, status-bar layout, file monitoring, Save/Save As, and RTF functionality are unchanged.

The targeted x13.4 QA covers both backing warnings, unrelated warnings, routine-message suppression, recovery behavior, and AST preservation of unrelated methods. Static source gates are provided; live Fedora KDE/PyQt6 interaction testing remains outstanding.

---

# RiqatonyPad 2.0.0-x13.3 — Message conventions (2026-10-24)

Directly from 2.0.0-x13.2. This release changes only status-message presentation and approved action message templates. Noncritical status messages last four seconds; unresolved critical status messages persist. Filename-only save notices and period punctuation follow the approved standard. RTF codec, file operations, editor interface, and drag/drop remain unchanged.

# RiqatonyPad 2.0.0-x13.2 — Eight-message cross-family parity (2026-10-24)

Added only the eight approved status-message events, using the existing editor message label: successfully opened document, successful Save, successful Save As, successful Rename, empty plain-text clipboard, Insert/Overwrite mode toggle, successful external-editor launch and successful containing-folder launch. Success notifications follow their established operations; protected Save Version As preserves its existing priority and wording, as do RTF compatibility warnings. Editor layout, RTF codec, document and file operations, menus and shortcuts are unchanged. Static QA only; Fedora KDE/PyQt6 live GUI testing remains outstanding.

---

# RiqatonyPad 2.0.0-x13.1 — Editor status-bar correction (2026-10-23)

- Two visible editor status widgets: flexible messages at the left, one permanent indicator label at the right.
- The indicator reads `Insert · Chars 1,240 · 100%` (illustrative), with middle dots only between editing, character-count and viewing groups.
- Keep existing numerical grouping, status-bar style, height, message timer/tooltip, editor update signals and RTF/file behavior. No extra per-field width reservations.
- No window-geometry changes; visual Fedora KDE/PyQt6 verification pending.

---

# RiqatonyPad 2.0.0-x13.0 — Editor status-bar field order (2026-10-23)

- Reorder existing editor-status widgets to Insert/Overwrite → total Chars → numerical Zoom % → independent Message. No added or removed fields.
- Preserve existing fixed widths, status-bar styling, height, margins, numerical grouping, updates, timers and message tooltips.
- No editor, RTF, file lifecycle, toolbar, search, or window-geometry changes.
- Static release verification; live Fedora KDE/PyQt6 geometry validation remains outstanding.

---

# RiqatonyPad 2.0.0-x12.5

Behaviour-preserving presentation extraction: relocate existing About, Quick Tour and Keyboard Shortcuts application methods into `widgets/about_dialog.py`, `widgets/quick_tour.py` and `widgets/keyboard_shortcuts.py`; consolidate the existing shortcut-search helper without changing its implementations. No dialog classes or unrelated changes.

# RiqatonyPad 2.0.0-x12.4 — Keyboard-shortcut helper convergence (2026-10-18)

- Relocated existing keyboard-shortcut query helpers to `widgets/shortcut_search.py`, preserving original implementations and user behaviour.
- Removed the original root-level helper without compatibility shims; updated imports and Windows/AppImage packaging paths.
- Kept document Find/Replace and editing code unchanged; updated version metadata, manifests and QA.
- No public README content edits beyond current-version references.

---

# RiqatonyPad 2.0.0-x12.3 — Widget-tree reorganisation (2026-10-18)

- Relocated existing graphical modules into `widgets/` and editor-specific components into `widgets/rwpyn/`, without changing application/editor class methods.
- Updated imports, the RiqatonyPad resource-root lookup where applicable, build staging, active source QA and manifests.
- Kept application startup, document codecs and services outside the widget folders; no compatibility shims were added.
- Preserved GitHub root and internal README content apart from current version references. Live Qt/AppImage/Windows builds remain unverified.

---

# RiqatonyPad 2.0.0-x12.2 — Python shebang consistency (2026-10-18)

- Added the standard Python 3 shebang to three existing import-only Python modules; their previous contents and all methods remain unchanged.
- Preserved executable permissions and source paths; no widget-directory relocation or editor behavior changes.
- Updated release metadata, QA and source integrity manifest. Public README changed only for the current version.

---

# RiqatonyPad 2.0.0-x12.1 — Packaging layout and provenance cleanup (2026-10-18)

- Removed obsolete `OFFICIAL_SOURCE.md`; retained existing integrity verification and source history.
- Relocated Windows portable builder and supporting files to `packaging/windows/`, updating only build-root and release-version references.
- No editing, document, file-safety, or user-interface changes. Live Windows build remains unverified.

---

# RiqatonyPad 2.0.0-x12.0 — Application module filename convergence (2026-10-18)

- Renamed the standalone application module from `riqatonypad.py` to `app.py`, retaining original application/editor method implementations except for current version metadata.
- Updated portable launcher, Fedora AppImage/Windows staging, QA and source manifest without leaving the obsolete module.
- Set root `main.py` executable (`755`) while keeping its Python code unchanged other than the required entry-module filename.
- GitHub root README updated only for current release version; existing release records are untouched below.

# RiqatonyPad 2.0.0-x11.0 — Preservation correction (2026-10-17)

This is a restricted correction to the existing x10.0 extraction baseline. It fixes the Suite icon reference, restores original historical Ricopad review/provenance documentation, restores prior executable permissions, updates the current documentation index, and restores the original private inline-rich-text clipboard MIME string. The independent RiqatonyPad configuration namespace stays unchanged.

No RTF codec, editor-method body, document lifecycle, Ribbon/command artwork, x1–x10 historical fingerprint fixtures or Windows configuration logic was modified. Prior release history below is retained unchanged.

## RiqatonyPad 2.0.0-x10.0 — Editor file-lifecycle extraction only (2026-10-16)

Moved existing editor-owned file I/O, Save/Save As and related lifecycle methods into editor_lifecycle.py, without changing their definitions or operation; full original editor AST parity checked.

## RiqatonyPad 2.0.0-x9.0 — Platform/resource and startup-support extraction only (2026-10-16)

- Relocated the existing standalone `register_window`, Windows organisation migration, configuration-path, Windows desktop identity, theme-resource lookup and `main()` startup/probe functions into `editor_platform_startup.py`, preserving all six original AST definitions exactly.
- The original `riqatonypad.py` remains the execution entry point. Its thin `main()` forwarding adapter supplies the existing live window class, startup modes, palette/resource bindings and window registry to the unmodified startup implementation; source/Portable launch semantics are preserved.
- The extracted resource functions remain beside the original source folder, retaining relative path resolution. Both Linux AppImage and Windows source staging include the new module.
- No editor, RTF, Ribbon/Retro, command, file-safety or preference method changed. No shared runtime dependency and no opportunistic fixes.
- Retained the prior x1–x8 parity checks; the x9 gate additionally pins every moved helper and every editor method to x8.

## RiqatonyPad 2.0.0-x8.0 — Commands, icons and appearance extraction only (2026-10-16)

- Relocated the existing 28 command/icon/appearance methods into `editor_commands_appearance.py` without changing their parsed definitions.
- Relocated the unchanged Ribbon/Retro shared command inventory and default selection into the same module, importing the identical objects through the editor host.
- Kept all host event handlers, document/file logic and existing Ribbon/Retro presentation extraction unchanged. No shared-runtime dependency or behaviour changes.
- Retained x1–x7 extraction QA and added frozen x8 method parity; actual GUI/packaged runtime remains for host validation.

## RiqatonyPad 2.0.0-x7.0 — Ribbon and Retro presentation extraction only (2026-10-16)

- Relocated the original RibbonScrollArea class and 24 unmodified Ribbon/Retro presentation methods into editor_ribbon_retro.py.
- Kept the canonical command inventory and action creation unchanged in riqatonypad.py; existing interface constants were re-exported.
- No UI/shortcut/command behaviour, document formatting, file lifecycle, shared runtime or RTF codec changes.
- Preserved exact x6.0 AST fingerprints and retained earlier x1–x6 gates; Qt runtime and actual builds require host verification.

## RiqatonyPad 2.0.0-x6.0 — Preferences and new-document defaults extraction only

Original preferences and new-document defaults extracted without changes; historical release details retained below.

## RiqatonyPad 2.0.0-x5.0 — Printing, PDF and document information extraction only (2026-10-16)

Relocated ten existing page setup, print/PDF, file-size/date and Properties methods unchanged into `editor_printing.py` using the same host method names. Relocated their existing supporting constants and functions without changing ASTs and preserved imports through the editor host. All previous x1–x4 method definitions remain unchanged. No user-visible feature, file lifecycle, RTF codec or runtime sharing changes. Live Qt and actual packaged builds still require host verification.

## RiqatonyPad 2.0.0-x4.0 — Find/Replace and editor-view extraction only (2026-10-16)

Moved 40 existing Find/Replace, search-state, zoom, word-wrap and tab-width methods into an application-local `editor_search_view.py` mixin without altering any method definition. The existing search cap moved with those methods; all previous stage method contracts remain intact. No feature, user-facing behaviour, configuration, RTF/file lifecycle or workspace changes. Live Qt and actual packaged builds remain for target-host verification.

## RiqatonyPad 2.0.0-x3.0 — insertion and clipboard extraction only (2026-10-16)

Moved 39 existing symbols, image/link/table, clipboard, line editing, and date/time insertion methods verbatim to `editor_insertion.py`. Moved their three exclusively used image safety limits and two unchanged helper functions into the same module, importing them back into the host to preserve existing names. No new features, behaviour changes, shared runtime dependency, or RTF/file-lifecycle algorithm changes. x1 and x2 extraction contracts retained. Qt runtime and actual packaged builds still require host verification.

## RiqatonyPad 2.0.0-x2.0 — formatting extraction only (2026-10-16)

Relocates 43 existing rich-text formatting methods into an application-local `editor_formatting.py` mixin. No method-body changes, cross-application shared dependency, new functionality, or altered document/file-lifecycle behaviour. Preserves x1.0 widget extraction; updates source packaging and location-aware regression checks. Live Qt runtime and AppImage/Windows builds must be verified on equipped hosts.

# RiqatonyPad 2.0.0-x1.0 — Editor widget extraction

Based on 1.1.2. Moved `SafeTextDocument` and `RichTextEdit` verbatim to `editor_widgets.py`; retained public import names and application-specific widget behaviour. Updated only required module loading, packaging, release identity and verification wiring. No editor features or file-lifecycle changes.

---

# RiqatonyPad 1.1.2 — Public identity migration from Ricopad 1.0.15

This release rebrands the existing Ricopad 1.0.15 application as RiqatonyPad without replacing or relocating its RTF engine or codec. The original document workflows, external-change protection, Ribbon/command icon families, menus, shortcuts and file-safety algorithms remain in place.

Updated identities: RiqatonyPad application/window-list name, `riqatonypad` executable, desktop entry, Suite component ID, GitHub repository, Windows identity, AppStream, About and documentation; `riqatony_pad/` Python source folder; independent preferences namespace; and the exact supplied RiqatonyPad application icon assets.

The KDE Plasma window-list identification follows the confirmed MaqaronyPad application naming/desktop-entry approach: Qt application name **RiqatonyPad**, Qt desktop-file name `riqatonypad`, and `StartupWMClass=RiqatonyPad`. The main document title-bar behavior remains unchanged apart from the product name.

The Fedora AppImage and Windows packaging retain Ricopad's original builder mechanics, with renamed paths and identities. The AppDir binary, plugin checks and documentation use consistent `riqatonypad` destinations. The source `riqatony_pad/` folder is not an AppDir library path.

Historic Ricopad 1.0.15 release notes are preserved byte-for-byte in `docs/history/Ricopad-1.0.15-RELEASE_NOTES.md`; pre-existing changelog entries remain historical. No Rwpyn modules or compatibility shims are included.

Qt/Plasma, Windows and complete Fedora AppImage builds still require target-system validation.

No RTF codec/serializer, rich-text support, document-format or file-lifecycle algorithms were modified.
