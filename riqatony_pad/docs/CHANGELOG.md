## RiqatonyPad 2.0.0 — Stable promotion (2026-11-01)

- Promote the unchanged 2.0.0-x16.9 runtime to the final 2.0.0 release version.
- Align application, Suite manifest, AppImage, Windows packaging, and release-check version metadata.
- Preserve the protected GitHub README except for its current-release version; preserve every prior change-history entry.
- No RTF/editor operation, Qt widget, icon asset, dependency, builder behavior or file-safety changes.
- Fedora AppImage build and live KDE/Qt acceptance remain unverified in the source release environment.

## RiqatonyPad 2.0.0-x16.9 — Find/Replace command toggle (2026-11-01)

- Make the Find and Find/Replace command buttons reliably close their currently active panel on repeated clicks even when Qt transfers keyboard focus away from its input; switching to the other command still focuses its corresponding field.
- Preserve the protected GitHub README byte-for-byte except its authorized current-release version field; the separately requested Riqatony Desk README removal is NOT part of this release.
- Add a dependency-free behavioral test of the real search methods covering repeated actions with/without retained input focus and switching Find/Replace modes.
- No RTF codec, document lifecycle, icons, editor layout, file operation or packaging behavior changes.

## RiqatonyPad 2.0.0-x16.8 — Qt QA import compatibility after app.py migration (2026-11-01)

- Correct two active Qt-backed QA modules to import the current `app.py` host instead of removed `riqatonypad.py`. Preserve their existing assertions and test logic.
- Execute both RTF round-trip and highlight/clear QA inside the Fedora builder's isolated PyQt6 environment, regardless of system Python Qt availability.
- Add a mandatory dependency-free QA import-contract regression check (including a deliberate obsolete-import negative case) before PyQt6-dependent tests.
- No changes to application runtime modules, widgets, RTF codec, icons, or the GitHub README beyond the current-version field.

## RiqatonyPad 2.0.0-x16.7 — Fedora AppImage builder source-layout compatibility

- Correct stale top-level Python module-count requirement after widget extraction.
- Compile only existing runtime modules and QA; remove nonexistent `tools/` directory from compileall.
- Stage all current runtime Python modules, including Unicode character counting and status-message conventions.
- Validate the actual builder preflight and staged import closure as part of the release gate.
- No editor/runtime behavior or icon-artwork changes.

## RiqatonyPad 2.0.0-x16.6 — GitHub README and Halcyon dark import icon correction (2026-11-01)

- Adopt the four GitHub README texts explicitly supplied in `updated-readme-2.zip` as the new protected authorities; only designated current-version field(s) differ in the issued release.
- Correct `impport-file.png` to `import-file.png` in the dark Halcyon family without changing any image bytes. Preserve all other icon assets and application functions.
- Enforce independent protected-README checking and exact Halcyon light/dark filename parity in the source-release gate.

---

## RiqatonyPad 2.0.0-x16.5 — Halcyon icons and protected GitHub README (2026-11-01)

- Add the fourth App Icons choice **Riqa Icons Halcyon**, with artwork from `ribbon-icons-aero`; AppMenu only (no selector icon or toolbar command). Persist choice and refresh all existing light/dark icon consumers.
- Restore the authoritative GitHub README; its **current version** field(s) are the only permissible modifications. Preserve recovered historical differences under `docs/history/` and enforce an independent immutable README gate.
- Existing icon families, commands and editor/file behavior remain unchanged.

---

## RiqatonyPad 2.0.0-x16.4 — Quick Tour construction hotfix (2026-11-01)

- Restore four missing Qt imports in extracted Quick Tour; preserve seven-page content and behavior. Add executable construction/callback regression test. No unrelated changes.

## RiqatonyPad 2.0.0-x16.3 — Authoritative icon inventory and Pad command wiring (2026-10-31)

- Remove the 18 retained icon files absent from the supplied Harmony/Humility/Heritage light/dark packs. Each family now contains exactly 144 PNGs per theme, including the four later Heritage corrections. No icon files beyond the supplied inventories are retained.
- Assign `app-drag-and-drop.png` to the App Drag-and-Drop parent menu without mirroring the chosen option icon. Assign `layout.png` to Editor Layout in AppMenu and Ribbon/Retro shared command inventory.
- Assign `toolbar-tabbed.png` and `toolbar-classic.png` to the Ribbon and Retro radio actions throughout the AppMenu and shared toolbar presenters. Preserve their radio behavior and persisted layout setting.
- No editor/codec, document, Word Wrap, or Riqatony Desk changes.

## RiqatonyPad 2.0.0-x16.2 — Heritage corrective icon patch (2026-10-31)

- Replace only four supplied light/dark Heritage PNGs: `external-editor.png` and `launch-last-file.png`, retaining all other source and icon assets.

## RiqatonyPad 2.0.0-x16.1 — Riqa Icons Harmony / Humility / Heritage (2026-10-31)

- Re-patched three supplied icon families; renamed selectors, applied approved AppMenu/Find/heading/Link/policy icon wiring; left toolbar variant icons and remaining mismatches deferred.

## RiqatonyPad 2.0.0-x16.0 — Rico Icons Harmony (2026-10-25)

- Replace the previous default `assets/ribbon-icons` PNG collection with the authoritative Harmony pack used by RiqatonyDesk 1.0.0-x19.0: 148 light and 148 dark PNGs; keep all available established icon names and add 42 new names per theme.
- Rename the visible default family **Rico Icons Modern** to **Rico Icons Harmony** (App Icons, Ribbon, selection feedback and current help) while keeping the persisted `new` preference value compatible.
- Preserve the Classic and Legacy families byte-for-byte and keep the default icon directory and light/dark selection logic unchanged.
- Retire obsolete old-default icon documentation; continue shipping no SVG assets. Preserve character counting, warning protection, editor operations, file handling, layout and other runtime mechanics.

## RiqatonyPad 2.0.0-x13.5 — Unicode Chars and PNG-only assets (2026-10-24)

- Count extended Unicode grapheme clusters in the rich-text editor's user-facing **Chars** status while preserving source/RTF safety limits and existing layout.
- Cache grapheme totals by QTextBlock revision; cursor-only updates reuse cached results rather than scanning the document text.
- Remove all 636 SVG files and retire the two SVG regeneration scripts; retain every existing PNG unchanged.
- Adjust active icon QA, packaging records, provenance documentation and release metadata for PNG-only assets.
- Preserve x13.4's explicit backing-warning identity behavior and all other editing/file methods.

## RiqatonyPad 2.0.0-x13.4 — Backing-warning dismissal precision (2026-10-24)

- Tag backing-file disappearance and external-change critical messages at their original watcher call sites.
- Returning to normal backing state clears only a currently displayed backing-file warning, never an unrelated critical message such as RTF compatibility or a failed Save/Load.
- Preserve x13.3 status layout, display wording, four-second routine messages, critical-warning priority, and existing success/recovery notifications.
- No changes to the RTF codec, document/file transactions, watcher detection, editor controls, or command surface.
- Add a targeted warning-lifecycle regression test and method-preservation gate.

## RiqatonyPad 2.0.0-x13.3 — Message conventions

- Four-second standard for noncritical status messages; persistent unresolved critical warnings.
- Filename in successful Save and Save As; action-led duplicate, delete and rename confirmations.
- Complete-sentence punctuation, single confirmation per operation.
- RTF and UI operations unchanged.

## RiqatonyPad 2.0.0-x13.2 — Eight-message cross-family parity

- Added success feedback for Open, Save, Save As, Rename, Open in External Editor and Open Containing Folder.
- Added empty plain-text clipboard feedback and Insert/Overwrite toggle feedback.
- Kept preservation-specific Save Version As and RTF compatibility messages in precedence; no new messages for unsuccessful/cancelled actions.
- No layout, file operation, RTF codec, shortcut or unrelated functional changes. Added focused QA and updated version records.

---

## RiqatonyPad 2.0.0-x13.1 — Two-widget editor status correction

- Show messages on the left and a permanent right-aligned `Insert · Chars N · Zoom%` indicator on the right.
- Retain original styling, message semantics, number grouping and editor behavior.
- New current-source gate; all historical QA and release entries retained.

---

## RiqatonyPad 2.0.0-x13.0 — Editor status-bar arrangement (2026-10-23)

- Change only the existing status-bar widget order to Insert/Overwrite, Chars, Zoom %, Message.
- Keep all four widgets, existing presentation, fixed widths, independent messages, and number formatting.
- Update release identity, QA and source inventory without other functional changes.

---

## RiqatonyPad 2.0.0-x12.5 — High-level dialog-method extraction (2026-10-18)

- Relocated the original About, Quick Tour and Keyboard Shortcuts dialog methods unchanged from app.py into dedicated widgets modules, without creating dialog classes.
- Consolidated the existing pure shortcut-search helpers and dialog method into `widgets/keyboard_shortcuts.py`; no obsolete compatibility module.
- Updated explicit Windows/AppImage build staging, module imports and existing regression audits. No other application behavior changes.

---

## RiqatonyPad 2.0.0-x12.4 — Keyboard-shortcut helper convergence (2026-10-18)

- Relocated existing keyboard-shortcut query helpers to `widgets/shortcut_search.py`, preserving original implementations and user behaviour.
- Removed the original root-level helper without compatibility shims; updated imports and Windows/AppImage packaging paths.
- Kept document Find/Replace and editing code unchanged; updated version metadata, manifests and QA.
- No public README content edits beyond current-version references.

---

## 2.0.0-x12.3 — Widget-tree reorganisation (2026-10-18)

- Converged standalone Pad widget organisation under `widgets/` and `widgets/rwpyn/`.
- Kept original editing algorithms and class method definitions unchanged; updated imports, resource lookup, build references and source regression checks.
- No new features, dialogs, application constants, services or compatibility shims.

---

## 2.0.0-x12.2 — Python shebang consistency (2026-10-18)

- Added the standard Python 3 shebang to three existing import-only Python modules; their previous contents and all methods remain unchanged.
- Preserved executable permissions and source paths; no widget-directory relocation or editor behavior changes.
- Updated release metadata, QA and source integrity manifest. Public README changed only for the current version.

---

## 2.0.0-x12.1 — Packaging-layout and provenance cleanup (2026-10-18)

- Removed redundant `OFFICIAL_SOURCE.md`, retaining manifest and release-record checks.
- Moved Windows build files intact to `packaging/windows/` and corrected the builder’s application-root resolution.
- Updated only necessary release, packaging and QA references. No editor-method or runtime-feature changes.

## 2.0.0-x12.0 — Application module filename convergence (2026-10-18)

- Renamed the standalone application module from `riqatonypad.py` to `app.py`, retaining original application/editor method implementations except for current version metadata.
- Updated portable launcher, Fedora AppImage/Windows staging, QA and source manifest without leaving the obsolete module.
- Set root `main.py` executable (`755`) while keeping its Python code unchanged other than the required entry-module filename.
- GitHub root README updated only for current release version; existing release records are untouched below.

## 2.0.0-x11.0 — Bounded preservation and release-engineering corrections (2026-10-17)

- Corrected Suite manifest icon path to the existing `riqatony_pad/` master folder.
- Restored historical Ricopad review/provenance documentation verbatim from 1.0.15.
- Restored predecessor executable script permissions; no script contents changed for this purpose.
- Updated the current documentation index and release metadata.
- Restored the established private Ricopad inline-rich-text clipboard MIME value; copied/pasted content and editor methods unchanged.
- Retained the independent RiqatonyPad preference namespace and x1–x10 extraction history.

## 2.0.0-x10.0 — Behaviour-preserving editor file-lifecycle extraction

Original editor file-lifecycle method bodies moved without code rewrites; existing workspace ownership and file safeguards retained.

## 2.0.0-x9.0 — Platform/resource/startup support extraction only

- Six existing platform and launch-support functions relocated unchanged into `editor_platform_startup.py`; launcher and host bindings preserved.

## 2.0.0-x8.0 — Commands/icons/appearance extraction only

- Existing command, icon and application/editor theme methods relocated unchanged to `editor_commands_appearance.py`. Prior application behaviour retained.

## 2.0.0-x7.0 — Ribbon/Retro presentation extraction only (2026-10-16)

- Relocated the original RibbonScrollArea class and 24 unmodified Ribbon/Retro presentation methods into editor_ribbon_retro.py.
- Kept the canonical command inventory and action creation unchanged in riqatonypad.py; existing interface constants were re-exported.
- No UI/shortcut/command behaviour, document formatting, file lifecycle, shared runtime or RTF codec changes.
- Preserved exact x6.0 AST fingerprints and retained earlier x1–x6 gates; Qt runtime and actual builds require host verification.

## 2.0.0-x6.0 — Preferences and new-document defaults extraction only

- Moved the eleven existing preferences and new-document defaults methods unchanged into `editor_preferences.py`.
- Preserved the existing settings schema, locations, startup application, generated template, and UI behaviour. No new features or behavioural changes.
- Original methods and helpers verified against the frozen x5.0 source fingerprints.

## 2.0.0-x5.0 — Printing, PDF and document information extraction only (2026-10-16)

Relocated ten existing page setup, print/PDF, file-size/date and Properties methods unchanged into `editor_printing.py` using the same host method names. Relocated their existing supporting constants and functions without changing ASTs and preserved imports through the editor host. All previous x1–x4 method definitions remain unchanged. No user-visible feature, file lifecycle, RTF codec or runtime sharing changes. Live Qt and actual packaged builds still require host verification.

## 2.0.0-x4.0 — Find/Replace and editor-view extraction only (2026-10-16)

Moved 40 existing Find/Replace, search-state, zoom, word-wrap and tab-width methods into an application-local `editor_search_view.py` mixin without altering any method definition. The existing search cap moved with those methods; all previous stage method contracts remain intact. No feature, user-facing behaviour, configuration, RTF/file lifecycle or workspace changes. Live Qt and actual packaged builds remain for target-host verification.

## 2.0.0-x3.0 — Behaviour-preserving insertion/clipboard extraction (2026-10-16)

- Moved 39 unchanged editor insertion and clipboard method bodies into `editor_insertion.py`.
- Preserved existing editor host interfaces, shared utilities via imports, RTF and file-lifecycle behaviour.
- Updated only required portable/AppImage/Windows module staging, metadata and QA source-location references.
- Preserved x1.0 widgets and x2.0 formatting AST parity gates.

## 2.0.0-x2.0 — Behaviour-preserving formatting extraction (2026-10-16)

Relocates 43 existing rich-text formatting methods into an application-local `editor_formatting.py` mixin. No method-body changes, cross-application shared dependency, new functionality, or altered document/file-lifecycle behaviour. Preserves x1.0 widget extraction; updates source packaging and location-aware regression checks. Live Qt runtime and AppImage/Windows builds must be verified on equipped hosts.

## 2.0.0-x1.0 — Behaviour-preserving widget extraction

- Relocated `SafeTextDocument` and `RichTextEdit` without editing class definitions or changing application behaviour.
- Preserved existing importing interfaces; updated necessary packaging and QA.

## 1.1.2 — RiqatonyPad public identity migration

- Rebrands the authoritative Ricopad 1.0.15 source without RTF engine/codec reshuffling.
- Uses the owner-supplied application logos and preserves all command/Ribbon artwork.
- Aligns Qt, Plasma desktop-entry and Suite identity with `riqatonypad`, GitHub and About.
- Preserves original AppImage/Windows builders with identity-dependent paths updated.
- Uses a clean, separate RiqatonyPad preference namespace; retains all existing RTF/file-safety behavior.
- Original Ricopad release history follows unchanged.

## 1.0.15 — App Drag-and-Drop parent icon synchronization

- Synchronized the AppMenu **App Drag-and-Drop** parent icon with the currently selected drag/drop radio option.
- Preserved the existing **Opens on Active Window / Opens on New Window** actions, persistence, and behavior unchanged.
- No RTF, lifecycle, Quick Tour, shortcut, layout, theme semantics, or unrelated changes.

## 1.0.14 — Quick Tour tooltip correction

- Corrected the actual Ribbon/Retro Quick Tour tooltip to **Quick Tour… — Shift+F1**.
- Preserved the existing Quick Tour menu label, page content, startup behavior, footer checkbox, navigation, and all unrelated behavior unchanged.

## 1.0.13 — bounded UI wording and Quick Tour footer refinement

- Aligned Line Spacing tooltips with Rico Plus.
- Relabelled **Paste Plain Text** to **Paste as Plain Text**.
- Added the ellipsis to the **Quick Tour…** tooltip.
- Moved the existing startup-suppression checkbox from the first Quick Tour page into the footer row, aligned left; navigation controls and all seven tour page title/body strings are unchanged.
- No RTF, lifecycle, layout/shortcut behavior, theme, icon-size, Clear Colour, workspace, or unrelated changes.

## 1.0.12 — Quick Tour startup/presentation refinement

- Increased visible Ribbon/Retro command icons to 36×36 within the existing 52×52 controls.
- Relabelled the Help menu command to **Quick Tour…**.
- Quick Tour now remains startup-enabled until **Don't show Quick Tour on startup again** is selected; the existing preference stores that choice and manual Quick Tour can re-enable startup display.
- Hid Back on the first Quick Tour page.
- Preserved all seven existing Quick Tour page titles/body strings exactly.
- No Clear Colour, workspace-wizard, RTF, lifecycle, layout/shortcut, theme-engine, or unrelated changes.

## 1.0.11 — shortcut/layout refinement

- Exposed the existing Highlight dialog keybinds in the button labels, including **Clear Highlight (Backspace)**.
- Restored `Ctrl+1/2/3/4` to Line Spacing 1.0/1.15/1.5/2.0.
- Reordered/relabelled Editor Layout to Toolbar Top / Find Bottom, Toolbar Top / Find Top, Toolbar Bottom / Find Top, Toolbar Bottom / Find Bottom.
- Assigned those layouts `Ctrl+Alt+Shift+1/2/3/4` respectively and made Toolbar Top / Find Bottom the unsaved/default layout.
- Removed App Theme `Ctrl+Alt+Shift+1/2/3`; retained `Ctrl+Alt+Shift+T` for Ribbon/Retro.
- No Clear Colour or unrelated behavior changes.

## 1.0.10 — keyboard and highlight-dialog interaction

- Added immediate-commit Highlight dialog keys: `Y/P/G/R/B/O/C/N` for Yellow/Pink/Green/Red/Blue/Orange/Cyan/Noir and `Backspace` for Clear Highlight.
- Relabelled highlight **Black** to **Noir** without changing its `#000000` value.
- Added App Theme `Ctrl+Alt+Shift+1/2/3` for Light/Dark/System.
- Replaced separate Ribbon/Retro `Ctrl+Alt+Shift+1/2` shortcuts with `Ctrl+Alt+Shift+T` toggle.
- Moved `Ctrl+1/2/3/4` from Line Spacing to the four existing Editor Layout actions; line-spacing behavior remains unchanged.
- Clear Colour is explicitly excluded.

## 1.0.9 — Audit 20 Help/Tour family alignment

- Renamed the user-facing **Tutorial Wizard** to **Quick Tour** across the command registry, AppMenu, tooltip and dialog title.
- Audited all existing Quick Tour pages against current Ricopad behavior; no content rewrite was required.
- Added a targeted Audit 20 regression gate; no Help behavior, editor, RTF, file-lifecycle, Ribbon/Retro mechanics or packaging mechanics changed.

## 1.0.8 — Audit 25 Ribbon Help/GitHub group-order convergence

- Swapped the existing Help-page Ribbon group order from **GitHub → Help** to **Help → GitHub**.
- Preserved every command, icon, shortcut, handler, URL, AppMenu entry and Retro behavior unchanged.
- Added a targeted Audit 25 regression gate; no editor, RTF, file-lifecycle, watcher, theme/icon or packaging-mechanics changes.

## 1.0.7 — Audit 23 Delete-preservation correction

- Ported Rico Plus 0.2.12 open-document Delete preservation into Ricopad: successful Delete removes the backing RTF but retains the live document in the existing `missing` backing-file lifecycle.
- Preserved the destructive-operation safety contract: a Save Version As path rebind cancels the pending Delete, discarded dirty edits are reloaded from disk before deletion, and existing pre/post-confirmation identity/signature checks remain intact.
- Added explicit Delete confirmation text that the open document will be retained so it can be saved elsewhere or recreated.
- Added a targeted Audit 23 regression gate; no RTF codec, formatting, Save/Save As semantics, Duplicate, Rename, watcher architecture, UI or packaging-flow changes.

## 1.0.6 — Audit 24 clean-load Undo/Redo correction

- Ported the exact Rico Plus 0.2.12 successful-load cleanup ordering into Ricopad: `clearUndoRedoStacks()` immediately before `setModified(False)`.
- Clean RTF loads no longer retain Qt undo/redo entries generated internally by document reconstruction/import.
- Added a targeted Audit 24 regression gate for the exact call presence and ordering.
- No RTF codec, formatting, Save/Save As, file-lifecycle, watcher, AppMenu, Ribbon/Retro, Find/Replace, Symbols, packaging-flow or build-script behavior changes.

## 1.0.5 — AppImage Light-theme smoke-test correction

- Corrected the stale AppImage GUI smoke expectation for Light mode from `#f5f6f7` to Ricopad's canonical `#D4D4D4` window colour.
- Kept the actual Light palette and the complete AppImage build/PyInstaller/AppDir pipeline unchanged.
- Updated only the minimum release/package identity, release records and regression assertion required for a new traceable release.
- No runtime editor, RTF, file-lifecycle, watcher, UI, menu, Ribbon/Retro, Find/Replace or Symbols changes.

## 1.0.4 — External backing-file survival

- Added explicit `normal / changed / missing` backing-state tracking on top of the existing standalone file + parent-directory watcher.
- Missing backing files now show dedicated warning text and disable Reload until a disk copy exists again.
- Added protected preservation for clean or dirty missing-backed documents: **Save Version As… / Recreate Original… / Close Without Saving / Cancel**.
- Recreate Original remains inside the existing protected Save conflict flow and therefore still requires explicit **Overwrite**.
- Applied missing-file preservation before close, New/Open/document replacement and Save and Exit; a synchronous signature check closes the timer-race window before discard.
- Added targeted Audit 3 QA and retained all 1.0.3 UI and 1.0.2 Find/Replace/Symbol parity gates.
- No RTF codec, rich-text formatting, AppMenu, Ribbon/Retro, Find/Replace, Symbols, Rename/Delete or Plus workspace-scaffolding changes.

## 1.0.3 — AppMenu cleanup

- Reordered File → More Actions to exact Rico Plus 0.2.9 order/wording and removed the separator after Save As.
- Relabelled Edit entries to Find and Find and Replace, retaining the 1.0.2 unified panel behavior.
- Reorganised View to the approved Full Screen / Show Status / Word Wrap / Dark Editor / Locked Mode / Editor Layout / Editor Toolbar / Editor Zoom / Editor Miscellaneous structure.
- Added approved Theme and Drag-and-Drop toolbar tooltip wording without changing Rico icon-family labels.
- Made bundled Documentation open Locked with a non-persistent pre-collapsed Ribbon when Ribbon mode is active.
- Added targeted 1.0.3 UI-cleanup QA; no file-lifecycle, RTF/editor or Find/Replace-engine behavior changed.

## 1.0.2 — Find/Replace and Symbols parity

- Ported the current unified transient two-row Find/Replace behavior from Rico Plus while preserving Ricopad's existing four Editor Layout placement modes and exact AppMenu labels.
- Added `Ctrl+F` / `Ctrl+H` focus-aware toggle behavior, `Esc` close, live Match Case, real active result selection, bounded result counts and replacement safety limits.
- Expanded the curated Symbol grid from 32 to 40 symbols with `★ ☆ ♥ ♦ ♣ ♠ ☐ ☑`.
- Added targeted Phase 2 QA and synchronized release/package identity at 1.0.2.
- No file lifecycle, watcher, Save/Save As, RTF codec or unrelated shell behavior changed.

## 1.0.1 — Duplicate File no-clobber safety

- Made Duplicate File refuse any destination that already exists.
- Made final duplicate installation race-safe/no-clobber: a file or symlink appearing after destination selection is preserved and duplication is cancelled.
- Retained same-directory temporary output, flush/fsync, source-mode preservation, 25 MiB reopen limit and all 1.0.0 editor/RTF/external-change behaviour.
- Added regression QA for the no-clobber contract and synchronised release/package identity at 1.0.1.

## 1.0.0 — Stable convergence closure

- Promoted the reviewed 0.9.1 runtime unchanged as the stable 1.0.0 baseline.
- Corrected stale current-release documentation that still described the earlier pre-audit and packaging-era state.
- Synchronized application, Suite, AppStream, Fedora AppImage, Windows portable, bundled help and QA release identity at 1.0.0.
- Corrected Windows fixed-file version metadata to 1.0.0.0.
- Added release-record consistency QA so key current-release documents and package identities must agree.
- No editor, RTF, file-lifecycle or UI behavior changes.

## 0.9.1 — External-change convergence

- Replaced the Ricopad-only proactive modal conflict prompt with the persistent Rico Plus-style external-change warning surface.
- Removed the proactive `Later` choice; unresolved conflicts remain visibly present until resolved.
- Retained Ricopad's protected save-time **Save Version As…** path.
- Made ordinary **Save As…** protected while a conflict is pending, including a post-dialog conflict recheck.
- Kept explicit **Overwrite** as the only route allowed to replace the externally changed source.
- Updated convergence/file-lifecycle QA and source metadata for the new traceable release.

## 0.9.0 — Shared implementation + Help cleanup

- Ported Rico Plus 0.0.4-r8 fuzzy Keyboard Shortcuts matching while retaining Ricopad's live QAction inventory and menu filter.
- Replaced Ricopad's private new-document RTF string builder with the same pure `NewDocumentDefaults` / `build_new_document_rtf_payload()` implementation used by Rico Plus.
- Cleaned About/Tutorial/Help content, including PyWordpad attribution/link, Microsoft WordPad-inspired wording, Configuration path wording, light-theme About links and current Ribbon/Retro/shortcut-search guidance.
- Deliberately deferred the wider Ricopad/Rico Plus parity audit and any additional fixes discovered by it.

## 0.8.9 — Retro parity + shortcut alignment

- Introduced one `COMMAND_SURFACE_SPECS` registry shared by Ribbon and Retro for command identity, QAction/menu ownership and Rico icon names.
- Extended **Customise Retro Bar…** to the complete applicable shared command inventory, including menu-backed selector buttons.
- Changed the curated Retro default to New / Open / Save / Undo / Redo / Font Face / Font Size / Bold / Italic / Underline / Highlight / Text Colour / Bullet List / Align Left / Align Centre / Indent / Image / Table / Find and Replace.
- Swapped shortcuts: Highlight Colour `Ctrl+Shift+H`, Horizontal Rule `Ctrl+Alt+Shift+H`, Paragraph… `Ctrl+Shift+P`, Export PDF… `Ctrl+Alt+Shift+P`.
- Preserved the three exact 106-command Rico icon families and all 0.8.8 editor, RTF, file-lifecycle and Configure/AppMenu behavior.

## 0.8.8 — Configure/AppMenu cosmetic rework

- Reworked Configure and AppMenu organization to the approved standalone layout without changing editor/file behavior.
- View now owns Editor Layout and Editor Toolbar selectors; Settings owns App Theme, App Icons, App Drag-and-Drop and the two dirty-state policy selectors.
- Configure App Settings uses the final swapped rows: New Window / Open Externally above Active Window / Duplicate File.
- Reused existing Rico-family assets for all new selector surfaces; no new artwork was introduced.
- Removed `assets/ricopad-icons/` and the special `layout-retro` runtime/packaging path. Production command icons now come exclusively from the three exact 106-command Rico families.
- Preserved 0.8.7 transactional Save As, external-change watching/conflict handling, safer rename/delete, and dirty-state workflow behavior unchanged.
- Postponed the planned deeper implementation-convergence phase.

## 0.8.7 — file lifecycle and external-change convergence

- Corrected the editor status bar to the Rico Plus order: **Insert/Overwrite → Zoom → Chars → Message**.
- Ported transactional Save As: the target is written independently before Ricopad adopts the new path.
- Added standalone file/directory watching with debounced exact-byte checks so external edits, replacements and deletions are detected while the document is open.
- Added **Save Version As…** for external-change conflicts; the externally changed source path is forbidden as the preservation target.
- Hardened Rename/Delete with pre-operation identity/content checks and no-replace rename semantics.
- Added explicit dirty-state Duplicate choices: **Duplicate Current Document** or **Duplicate Last Saved Version**.
- Added explicit dirty-state External Editor choices: **Save Changes and Open** or **Open Last Saved Version**.
- Both dirty workflows default to **Ask Every Time**, can remember a choice, and can be reset under Settings → File Handling.
- Preserved the 0.8.6 command-surface/Locked Mode/Full Screen/title/Properties work, all three exact Rico icon families, and the existing RTF/editor core.

## 0.8.6 — shared command-surface and generic shell parity

- Added a dedicated Settings AppMenu and aligned shared File/Edit/View structure with Rico Plus 0.0.4-r8.
- Properties moved to File → More Actions and gained F4; Find Bar is now explicitly present in Edit.
- Aligned Duplicate shortcuts: Ctrl+D Duplicate Line / Selection; Ctrl+Shift+D Duplicate File.
- Ribbon Home drops Advanced; Insert gains the shared Advanced group; View becomes Configure with View Control / Editor Settings / Theme Settings / App Settings.
- Renamed user-facing View Only to Locked Mode and ported the guarded disable dialog with persistent “Don't ask again”.
- Added Full Screen (F11). Focused Mode remains intentionally Plus-only.
- Window title now carries current-folder context; status bar drops filepath/column and uses Insert/Overwrite, Chars, elastic timed message, and zoom.
- Properties adds on-demand Unicode-aware Word Count while retaining Location and Full path.
- RTF codec and rich-text support remain unchanged. File-lifecycle convergence is deferred to 0.8.7.

## 0.8.5 — Phase 1D icon-family parity

- Ported Rico Plus 0.0.4-r8's complete **Rico Icons Modern**, **Rico Icons Classic**, and **Rico Icons Legacy** families byte-for-byte, including all 106 commands in light/dark PNG and SVG forms.
- Kept technical family keys `new`, `classic`, and `original`; Modern remains the default and existing saved `new`/`classic` choices remain compatible.
- Reordered the selectable icon families to **Modern → Classic → Legacy**.
- Kept Ricopad-only `layout-retro` artwork separate from the imported Rico family trees so the upstream asset sets remain exact.
- Preserved 0.8.1 shortcuts, 0.8.2 command layout, 0.8.3 Light defaults/palette, and 0.8.4 live theme-switch behavior unchanged.

## 0.8.4 — Phase 1C completion

- Ported Rico Plus 0.0.4-r8's live theme-switch re-polish contract into standalone Ricopad.
- Ribbon section borders now use `palette(mid)` instead of a colour sampled and frozen when the Ribbon is constructed.
- Persistent Ribbon and Retro command surfaces are explicitly unpolished/re-polished after App Theme changes.
- Preserved independent editor-canvas theming, 0.8.3 Light defaults/order, prior shortcut/menu parity, icon assets, About, RTF/editor behavior and file workflows.
- Added a dependency-free live theme-switch parity gate.

## 0.8.3 — Phase 1C

- Ported the canonical Rico Plus 0.0.4-r8 Light application palette to Ricopad.
- Fresh profiles now start with Light App Theme and a Light editor canvas.
- Reordered App Theme to Light → Dark → System.
- Preserved explicit saved theme/canvas choices, all 0.8.1 shortcuts, the 0.8.2 Format/Insert layout, icon assets, About, RTF/editor behavior and file workflows.
- Added a dependency-free Phase 1C theme-parity gate.

## 0.8.2 — Phase 1B

- Aligned Ricopad Format and Insert AppMenu/Ribbon command grouping with Rico Plus 0.0.4-r8 for shared commands.
- Removed standalone Clear Highlight from Format while preserving Clear Highlight inside the Highlight Colour dialog.
- Reordered Format to font/colour > effects > list/indent > paragraph controls > Clear Formatting.
- Reordered Insert to Image/Link > Tables > Date/Time > Horizontal Rule/Symbol.
- Rebuilt the Insert Ribbon groups as Images & Links, Tables and Classics; moved Clear Formatting and Horizontal Rule into Classics.
- Preserved the complete 0.8.1 shortcut map, RTF/editor behavior, themes/defaults, icon families, About and file workflows.
- Added a dependency-free Phase 1B menu/Ribbon parity gate.

## 0.8.1 — Phase 1A

- Aligned seven agreed keyboard shortcuts with Rico Plus 0.0.4-r8: Text Colour `Ctrl+Shift+C`, Font `Ctrl+Shift+F`, font size +/- `Ctrl+Shift+]` / `Ctrl+Shift+[`, Bullet List `Ctrl+Shift+L`, New Window `Ctrl+Alt+Shift+N`, Dark Editor `Ctrl+Alt+Shift+E`.
- Updated the two explicit Retro tooltips and the bundled F1 Bullet List shortcut; Ribbon/Retro actions remain shared.
- Retained Ricopad Duplicate File `Ctrl+D` and Duplicate Line / Selection `Ctrl+Shift+D` pending a separate decision.
- Added a scoped shortcut-parity regression gate; retained all existing RTF/editor, theme, icon, menu and packaging behavior.

## 0.8.0-r3

- Metadata-only alignment release; editor, RTF codec, Ribbon, themes, shortcuts, status bar and document workflow are unchanged from 0.8.0-r2.
- Added structured AppStream developer metadata for `io.github.brunonlinespace` / Bruno Machado.
- Added OARS 1.1 content-rating metadata.
- Reduced the AppStream release feed to the current `0.8.0-r3` release dated 2026-09-25; full release history remains in this changelog.
- Hardened built-in and static metadata QA to enforce the current AppStream contract.

# Ricopad changelog

## 0.8.0-r2

- Fixed the Highlight Qt runtime QA teardown used by the AppImage build: deliberately modified test windows now use Ricopad's existing controlled-close bypass instead of invoking the user-facing unsaved-changes prompt.
- This prevents an invisible modal Save/Discard/Cancel dialog from stalling off-screen AppImage QA after the Delete Line runtime test passes.
- No editor, RTF, Ribbon, Retro, shortcut, theme, status-bar or file-workflow behavior changes.

## 0.8.0-r1

- Fixed the Highlight Qt runtime QA used by the AppImage build so it no longer materialises `QTextFormat.properties()` into Python when Qt exposes opaque font-feature maps.
- The regression still compares the complete character format exactly, now through native `QTextCharFormat` copies/equality.
- No editor, RTF, Ribbon, Retro, shortcut, theme, status-bar or file-workflow behavior changes.

## 0.8.0

- Promoted the reviewed 0.7.3-exp1-r2 application behavior unchanged into the 0.8.0 packaging line.
- Added root `suite-pythoine-component.json` with authoritative Ricopad/Suite identity, version, `.rtf` routing, portable `main.py` entrypoint, icon, desktop ID, publisher and capabilities.
- Added builder validation of the Suite component manifest and records its SHA-256 in AppImage build provenance.
- Added a destructive-path guard requiring `BUILD_ROOT` to remain a child of `ricopad/build/`.
- Retained the existing hardened non-privileged Fedora 43/44 builder, x86_64/aarch64 support, RTF/Qt QA, theme/icon smoke matrix, final-AppImage extraction tests, appimagetool validation/pinning, checksums, build-info and Python lock.
- No editor, RTF, Ribbon, Retro, shortcut, theme, status-bar or file-workflow behavior changes.

## 0.7.3-exp1-r2

- Ported the validated Rico Plus 0.0.4-exp6 highlight-boundary correction into authoritative Ricopad.
- Highlight processing now reads the exact character being modified instead of the character immediately to its left at selection boundaries.
- Highlight runs preserve their full existing `QTextCharFormat`; clearing removes the background plus Ricopad-owned automatic contrast foreground/property only.
- Genuine user foreground colours and other character formatting remain intact.
- Added the unchanged three-file regression corpus plus focused static and Qt runtime coverage for first/middle/final boundaries, partial/dark highlight clearing, explicit colours and caret-word clearing.
- Kept the 0.7.3-exp1-r1 Delete Line correction and 0.7.3-exp1 RTF codec backport unchanged.

## 0.7.3-exp1-r1

- Ported the proven Rico Plus 0.0.4-exp3 Delete Line correction into Ricopad.
- Non-empty blocks now stop after `BlockUnderCursor` + `removeSelectedText()`.
- Explicit `deleteChar()` / `deletePreviousChar()` paragraph-separator deletion is reserved for genuinely empty blocks.
- Prevents middle paragraph/list-item deletion from merging neighbouring blocks.
- Prevents final non-empty paragraph/list-item deletion from consuming the last character of the preceding block.
- Added static regression coverage and six Qt runtime cases for middle/final, empty/non-empty and bullet behavior.
- Kept the 0.7.3-exp1 RTF codec backport unchanged.

## 0.7.3-exp1

- Reset the active experimental line to 0.7.3.
- Backported the approved Rico Plus empty-paragraph/cell RTF codec correction into authoritative Ricopad.
- Empty paragraphs/cells now snapshot final paragraph style and typing state before completion.
- Empty imported paragraphs explicitly restore their typing baseline so blank-document defaults survive reopen.
- Added dependency-free blank-paragraph alignment/line-spacing regression coverage.
- No unrelated UI, shortcut, theme, status-bar or workflow changes.

# Changelog

## 0.7.2 — pre-release candidate r5.4

- Treat constructor-time new-document default application as programmatic loading rather than a user edit.
- Restore both the Qt modified flag and Ricopad's save-state mirror before startup continues.
- Start with clean `Untitled.rtf`, prompt only after a genuine edit, and leave the same clean unbound fallback after a failed startup import.
- Keep malformed/zero-byte RTF rejection and the complete r5.3 codec, editing, interface, shortcut, theme and packaging baseline unchanged.
- Extend live Qt lifecycle coverage across untouched startup, first edit, File → New, failed import and blank Save As/reopen/resave.

## 0.7.2 — pre-release candidate r5.3

- Fix list-marker parser state leaking into sibling character-format groups, which removed intended spaces before bold, italic or other formatted runs and could continue into later paragraphs.
- Persist normal Indent/Outdent as RTF left-margin geometry while keeping each touched paragraph independent.
- Persist list Indent/Outdent as semantic `QTextListFormat` levels, detaching only selected items and rejoining an adjacent compatible parent list when outdented; keep resumed parent-list identity and nested geometry stable across repeated cycles.
- Preserve the r5.2 command surface, shortcuts, Ribbon/Retro layout, themes and packaging unchanged.
- Add dependency-free and PyQt regressions for mixed-format list spaces, post-list paragraphs, multi-cycle normal/list indentation, and blank first Save As/reopen/resave.

## 0.7.2 — pre-release candidate r5.2

- Preserve the r5.1 patched bullet codec and all document/RTF behaviour unchanged.
- Apply the reviewed shortcut map, including Ctrl+D Duplicate File, Ctrl+Shift+D Duplicate Line / Selection, Ctrl+1–4 line spacing, Ctrl+5 Bullet List, F12 View Only, and the revised formatting/file/help bindings.
- Remove shortcuts from Properties, Delete File, Page Setup, Increase/Decrease Font Size, Tab Width, New Document Defaults, App Drag and Drop choices, GitHub, Raise an Issue, and About.
- Reorder/relabel View to the reviewed App Theme / App Drag and Drop / More Settings structure and relabel Increase/Decrease Indent to Indent/Outdent.
- Add Markopad-style search/filtering to Keyboard Shortcuts.
- Derive Ribbon/Retro command tooltips from the shared QAction shortcut and add a shared toolbar right-click Ribbon / Retro / Customise Retro Bar… menu.

## 0.7.2 — pre-release candidate r5

- Freeze the r4 last-known-working document, interoperability, Ribbon/Retro, theme and packaging behaviour.
- Make Return spacing recovery conditional: native QTextEdit paragraph creation is left untouched when spacing already inherited correctly, especially across repeated trailing empty paragraphs.
- Synchronize View → Status Bar check state with the actual restored status-bar visibility.
- Explicitly focus the document canvas after normal Ribbon startup; first-run Tutorial retains focus while open and hands focus to the editor when closed.
- Add focused Qt/static regression coverage for repeated Return, status-action state, and startup-focus handoff.

## 0.7.2 — stabilization/interoperability candidate r4

- Freeze the successful r3 editing/interoperability behaviour; no broad editor or codec refactor.
- Remove Numbered List creation from Format, Ribbon, Retro, shortcuts and current documentation.
- Remove Go To Line from Edit, Ribbon, Retro, shortcuts/tutorial/documentation, and remove the line component from the status counter.
- Reorder Home exactly to the reviewed Clipboard, Font, Formatting, Paragraph and Advanced control layout.
- Emit standards-based RTF bullet lists with list tables, overrides and `ls`/`ilvl`; retain decimal-list codec coverage only for externally imported interoperability; add a LibreOffice-produced list fixture and headless LibreOffice interoperability gate.
- Make alignment, indent and line-spacing operations mutate each selected paragraph's own block format, preventing list/alignment contamination across mixed selections.
- Preserve explicit proportional line spacing when Enter exits a list without copying paragraph alignment or list identity.
- Materialise New Document Defaults exactly (family, size, bold/italic, spacing and alignment) and keep Normal/Clear Formatting/heading-exit baselines tied to the open document default font.
- Apply character formatting to the selection or current word; whitespace changes future typing format.
- Preserve list semantics for whole-item rich clipboard copy/cut.
- Add automatic highlight text contrast without serialising the display colour as an explicit RTF foreground.
- Replace Retro QToolBar/private extension overflow with one horizontally scrollable 52 px row using wheel/QScroller panning and no overflow arrow.
- Synchronise Word Wrap check state, centre Symbols, swap Increase/Decrease Indent order, and add standard paragraph alignment shortcuts.
- Open document/Help/About URLs through a cleaned host environment so final AppImages can reach the system browser/file manager.
- Restore the richer seven-page Tutorial content while retaining the safe modeless retained lifecycle.
- Add post-fix code review and expanded packaging/parity QA; candidate remains gated on target live PyQt6/AppImage testing.

## 0.7.1 — defaults/template and Help-dialog stability release

- Fix Tutorial Wizard and Keyboard Shortcuts on both Portable and AppImage: import the required Qt widget classes and replace local nested `exec()` lifecycles with retained, application-owned modeless dialogs that safely show/raise/reopen.
- Add repeated-open GUI smoke coverage for both Help dialogs.
- Replace external Markdown Documentation launching with bundled `docs/Ricopad-Documentation.rtf`, opened in a separate read-only Ricopad window; stage the RTF documentation inside Linux AppImage and Windows frozen payloads.
- Rename **Dark/Light Editor** to **Dark Editor Canvas** and make checked mean dark / unchecked mean light.
- Introduce a generated per-user `new-document-template.rtf`. Factory defaults are Sans Serif 12 pt, normal, 1.15 line spacing, left alignment.
- Replace **New Document Font…** with **New Document Defaults…** for family, size, style, line spacing and alignment. Changing defaults regenerates the template without reformatting an open RTF.
- New untitled documents are initialized by Ricopad's own bounded RTF import path from that template; existing RTF documents remain governed solely by their own RTF defaults and formatting.
- Retain the 0.7.0 RTF/list/table/save-reopen engine and Portable/AppImage parity work unchanged outside the new-document initialization boundary.

## 0.6.11.1 — canonical dual-icon/theme and in-house formatting hotfix

- Promote the former `0.6.11-iconset-exp4` branch to canonical mainline; retire the separate non-icon mainline direction.
- Expose Theme in portable/source and AppImage: System / Dark / Light, then Rico Icons Modern / Rico Icons Classic / Rico Icons Legacy.
- Apply the requested View/Edit menu labels/order, rename Interface to Toolbar, Reset to Reset Zoom, and Default Font to New Document Defaults.
- Make paragraph styles apply immediately to all selected paragraphs.
- Make Bullet/Numbered List create one coherent normalized list and remove stale hanging-indent state when lists are removed.
- Replace Clear Character Formatting with Clear Formatting: reset character + paragraph formatting while preserving links, images/objects, tables and page-break structure.
- Restrict New Document Defaults to brand-new otherwise-empty documents.
- Vertically centre Qt's native Retro overflow control in the 52 px grid.
- Replace the off-screen event-loop formatting parity probe with a synchronous semantic/serialization probe and run source/portable parity under System/Dark/Light before AppDir/final-AppImage comparisons.

## 0.6.11-iconset-exp4 — former experimental parity branch

- Superseded by 0.6.11.1 promotion.


## 0.6.10-iconset-exp3 — experimental square-control geometry hotfix

- Keep canonical Ricopad 0.6.10 untouched and retain the exp2 AppImage System/Dark/Light × Classic/New experiment.
- Enforce one interface grid across Ribbon and Retro: every regular command button and compact selector is exactly 52 × 52 px; Font Family is exactly 104 × 52 px.
- Make Qt's native Retro overflow button use the same 52 × 52 px envelope.
- Replace the Ribbon's hard-coded 188 px expanded minimum with content-derived height based on real section size hints, tab-bar height and reserved native horizontal-scrollbar extent.
- Make Ribbon sections vertically fixed to their measured contents so active System/Fusion/Breeze style metrics cannot squeeze the two control rows.
- Derive Retro's outer toolbar height from the 52 px controls plus active native/QSS margins rather than hard-capping it before style polish.
- Re-run geometry normalization after AppImage theme changes and relevant style/layout events.
- Extend the existing AppDir/final-AppImage 3-theme × 2-icon smoke matrix to verify both Ribbon and Retro control dimensions.
- Retain the complete canonical 0.6.10 RTF/list/table-cell fidelity core unchanged.


## 0.6.9 — LibreOffice dirty-rewrite fidelity hotfix

- Resolve supported paragraph and character stylesheet inheritance before materialising imported RTF, preserving LibreOffice Normal/Body Text/Heading/Preformatted font families, point sizes, emphasis and paragraph spacing during an edited rewrite.
- Parse primary font names even when a LibreOffice font-table entry contains a nested `\*\falt` fallback group.
- Preserve imported simple-table `\cellx` column boundaries plus row-left/gap metadata through the live QTextTable and canonical RTF serializer instead of rebuilding equal-width columns.
- Add semantic clean-state fingerprinting so type/delete net-zero edits retain the exact original foreign RTF bytes and do not trigger the compatibility rewrite warning.
- Add a LibreOffice-style stylesheet/table regression fixture and build-host Qt dirty-rewrite assertions.
- Keep the 0.6.8-r1 paragraph-cycle, image-provenance, printing, safety, UI and packaging baseline unchanged.

## 0.6.8-r1 — Qt RTF QA fixture hotfix

- Application version remains **0.6.8**; no editor, RTF codec, UI, printing or packaging behavior changes.
- Correct the build-host repeated-paragraph Qt regression fixture: three `insertBlock()` calls are required to create two empty paragraphs before inserting the following text.
- Add explicit fixture-shape diagnostics so a malformed regression test cannot masquerade as an RTF fidelity failure.

## 0.6.8 — repeated RTF save/open fidelity hotfix

- Import supported RTF directly into QTextDocument structure instead of routing normal documents through HTML normalization.
- Preserve consecutive empty paragraphs, paragraph geometry and LibreOffice `\lin`/`\rin` indentation across repeated save/reopen cycles.
- Mark Qt-generated table separator blocks so they are not emitted as extra RTF paragraphs.
- Make an unchanged Save a no-op and an unchanged Save As an exact source-payload copy.
- Preserve original embedded/inserted PNG and JPEG bytes instead of silently converting every image to PNG on save.
- Keep canonical 0.6.7 icons; the separate icon-set experiment remains isolated.

## 0.6.7 — RTF metadata and Tables & Lines label hotfix

- Rename Insert Ribbon section **Tables** to **Tables & Lines**.
- Reaffirm Linux desktop/AppStream metadata as RTF-only (`text/rtf`, `application/rtf`) and add stronger release assertions against stale Markdown identity/format metadata.
- Retain all 0.6.6 RTF, interface, printing, safety, theme-policy and packaging behaviour unchanged.

## 0.6.6 — Ribbon caption alignment hotfix

- Keep Ribbon section captions below their sections, italic, and at the compact 0.6.5 size, but change alignment from left to right.
- Retain all 0.6.5 RTF, Retro, printing, safety, theme-policy and packaging behaviour unchanged.

## 0.6.5 — Ribbon/Retro polish hotfix

- Left-aligned Ribbon section captions and made the caption font slightly smaller and italic while keeping caption placement/style otherwise unchanged.
- Removed Retro group separators.
- Normalized Qt's native Retro overflow extension button to align with the 52 px command row.
- Kept **Customise Retro Bar…** permanently available in View → Interface.
- Retained the 0.6.4 RTF-only document, printing, safety and packaging baseline unchanged.

## 0.6.5 — interface simplification and native Retro overflow

- Restrict application-chrome Dark/Light choices to AppImage; portable/source/Windows return to host/system-only chrome.
- Move AppImage Dark Theme / Light Theme radio actions into View → Interface above Ribbon/Retro.
- Purge rich-text line numbers and their gutter/assets/preferences.
- Standardize Zoom as Zoom In / Reset / Zoom Out in View and Ribbon View Control.
- Move Dark Editor Canvas between Interface and Layout and remove the Tab Width/Default Font separator.
- Move compact Ribbon section captions below their sections and right-align them.
- Replace the broken custom Retro expansion surface with Qt native QToolBar overflow.

## 0.6.3 — Retro overflow and rich-editor UI correction

- Replace Retro horizontal scrolling with an expandable overflow arrow/panel while retaining Ricopad's existing icon-only controls and customization.
- Normalize Retro toolbar top/bottom padding.
- Reduce only Ribbon section-label font size; preserve label position, colour and styling.
- Relabel Insert section **Classic** to **Classics**.
- Make rich-document line-number painting table-aware so multiple cell blocks do not overprint the gutter.
- Keep the Ribbon font-family field scrolled to the beginning of the current family name after programmatic format synchronization.
- Make **Delete Line** remove the final logical line as well as middle lines.
- Make System theme icon selection follow the original host palette when returning from forced Light/Dark, including a deferred refresh for lazily polished platform styles.
- Keep the line-number gutter palette/repaint synchronized with the independent Dark Editor Canvas toggle.

## 0.6.2 — live-test editing/UI/theme refinement

- Normalize only automatic/unset body foreground to black on Print/PDF while preserving
  explicit RTF colours.
- Repair editor-viewport RTF drag/drop.
- Make font-size stepping selection/run aware.
- Replace the full Highlight Colour wheel with a compact standard palette + Custom + Clear.
- Apply the approved Ribbon and Global Menu reorganization, including a dedicated Insert tab.
- Add missing link/table editing icons and extend Retro customization to those controls.
- Add persistent rich paragraph line numbers and four Interface/Find workspace layouts.
- Add distribution-independent Overall Theme System/Dark/Light, with System disabling forced
  AppImage theming and Dark/Light available in portable/source builds.
- Keep Ricopad RTF-only; the submitted `Paste as Markdown` item resolves to Paste Plain Text.

## 0.6.1 — RTF fidelity and UI hotfix

- Refresh file-dependent actions immediately after first save/rename.
- Prevent/canonicalize duplicate inherited horizontal-rule blocks.
- Correct Qt-pixel/RTF-twip paragraph geometry and line-height-type serialization.
- Restore the modeless Pad-family About dialog.
- Remove redundant RTF status-bar field and place Find before Status Bar in that release.

## 0.6.0 — RTF-only product reset

- Focused Ricopad exclusively on Rich Text Format editing.
- Split rich-text safety and RTF parsing/serialization into dedicated modules.
- Fixed unset Qt brushes being serialized as explicit black foreground/highlight.
- Added compatibility reporting/warnings, persistent View Only/Ribbon state, QScroller touch,
  native Retro menus, and Nuxpad-informed printing/PDF pagination.

## 0.5.0

Preserved separately as the final mixed-format Ricopad line and fork seed for Markopad.
