# Ricopad 0.7.2 post-fix code review

Date: 2026-08-12
Baseline: exact uploaded Ricopad 0.7.1 canonical source tree
Review target: 0.7.2 stabilization candidate

## Review intent

This review was performed **after** the targeted 0.7.2 bug fixes, before release promotion. The priority is dependable current behaviour and external RTF interoperability. Historical Ricopad-specific encodings are not treated as constraints on the new output format.

## Areas reviewed

- RTF parser/serializer list model and safety bounds
- QTextDocument list construction and paragraph formatting scope
- new-document default materialisation and Normal/heading baselines
- rich clipboard list copy/cut paths
- character formatting selection/current-word semantics
- automatic text colour + highlight serialization
- Retro/Ribbon geometry and touch/wheel input routing
- QAction checked-state synchronization and focus restoration
- document/Help/About external URL paths under AppImage
- Tutorial/Keyboard Shortcuts lifecycle
- source/package version identity, manifests and QA hooks

## Findings fixed during review

### 1. Document-default bold/italic could still be lost by “normalising” paths

The first defaults fix correctly set a bold/italic document baseline, but several existing “Normal” assumptions still forced normal weight/roman style. `Normal` paragraph style, Clear Formatting baseline and heading-exit reset were updated to derive weight/slant/family/size from `QTextDocument.defaultFont()` instead. This makes the selected new-document style an actual document default, not merely an initial typing state.

### 2. Word-under-caret behaviour needed to be consistent, not font-size-only

The initial fix covered font increase/decrease. Review broadened the rule to the common character-format pipeline: Font Face/Size/Weight, bold/italic/underline/strike, super/subscript, text colour and highlight now use selection first, then the current word, while whitespace changes future typing. The packaging formatting-parity probe now includes a current-word assertion.

### 3. About-dialog links bypassed the cleaned AppImage host launcher

GitHub/Issue actions and document hyperlinks had been moved to `_open_host_target()`, but the About dialog still used QLabel automatic external opening. Review disabled QLabel direct external launch and routed `linkActivated` through the same cleaned host environment.

### 4. Nested-list body geometry could contradict its declared list level

The standards-based serializer emitted nine declared list levels, but body `li` geometry initially used the level-0 value even when `ilvl` was greater than zero. Review changed the body geometry to derive its left indent from the active list level, preventing an explicit body override from defeating the list-table level in external readers.

### 5. Retro retained an unused `QToolBar` import after removing toolbar overflow

The unused import was removed so the implementation boundary matches the architecture: Retro no longer depends on QToolBar at runtime.

## Interoperability validation performed

The dependency-free parser successfully imports a real LibreOffice-generated RTF containing standard list tables and reconstructs separate unordered/ordered list identities.

As a direct control, the user's `testing-0.7.1.rtf` converts successfully in LibreOffice but its ODT contains **zero** semantic `text:list` objects and zero list items, confirming the reported 0.7.1 interoperability defect rather than a mere Ricopad display issue.

The 0.7.2 standards-based list fixture was then converted headlessly by LibreOffice to ODT. The resulting ODT contains two semantic list objects and four list items.

The exact-default fixture (Noto Serif, 18 pt, Bold, Right, 2.0) was converted by LibreOffice to ODT and preserved the expected font family, point size, bold weight, right/end alignment and 200% line height.

Security/hostile-input QA, the 19-fixture RTF semantic corpus, Retro scroll-row QA, 53-method runtime callback audit and dual icon-family audit pass in the available environment.

## Review conclusion

No additional source-level release blocker was found after the fixes above. The design now has clearer state ownership: character formatting is selection/word-scoped, paragraph formatting is block-local, lists are standards-identified, new-document defaults are document state, and host integration is explicit.


## Post-test correction after first Fedora/Suite attempt

The first 0.7.2 stabilization archive was **not** acceptable for release promotion. The first live source launch exposed an `AttributeError` for `_schedule_interface_geometry_refresh`, and review then found `_refresh_ribbon_geometry` had been removed at the same edit boundary. Both methods existed in 0.7.1 and were unintentionally swallowed while replacing the old QToolBar overflow implementation. The intended removal at that boundary was only `_normalise_retro_extension_button`.

This was a review-process failure, not a Qt quirk: Python syntax/static checks cannot detect a missing dynamically accessed instance method by themselves. The callback audit is now hardened so every direct private `self._...()` call must resolve to a real Ricopad method. Static QA also explicitly requires `_schedule_interface_geometry_refresh`, `_refresh_ribbon_geometry`, `_refresh_retro_geometry`, and `_refresh_interface_geometry`. A method-inventory comparison against 0.7.1 now leaves only the deliberately retired `_normalise_retro_extension_button` absent.

The first Fedora/Suite AppImage attempt also stopped in LibreOffice QA on right alignment. The RTF fixture itself correctly contains `\\qr`, but the QA expected one exact ODT spelling, `fo:text-align="end"`. LibreOffice versions may serialize the same logical right alignment as `end` or `right`. The interoperability gate now parses the generated ODT, resolves the paragraph/text styles, and validates semantic formatting on the actual `Default test` paragraph. It accepts the two equivalent right-alignment serializations while still requiring exact Noto Serif, 18 pt, Bold, and 200% line height.

After these corrections, the dependency-free/full static gate passes again, including LibreOffice conversion, security QA, the 19-fixture RTF corpus, Retro scroll-row QA, the strengthened runtime-method audit, dual icon-family QA, and manifest verification. PyQt6/live GUI and final-AppImage gates remain mandatory on the Fedora host before release promotion.

## Remaining mandatory release gates

PyQt6 is not installed in this review container, so the real Qt-backed `qa/qt-rtf-qa.py`, `--ricopad-format-parity-probe`, GUI smoke, clipboard behaviour, focus behaviour and touch arbitration cannot be executed here. These are **not waived**. They must pass on the target build host and final AppImage.

Before canonical promotion:

1. Build/run the source/portable candidate with PyQt6 and complete `QA_TEST_PLAN.md`.
2. Run `qa/qt-rtf-qa.py` and the formatting-parity probe.
3. Exercise bullets/numbers and mixed line spacing with the user's original failure workflow, then open the saved RTF in LibreOffice.
4. Exercise Retro wheel/touch/tap behaviour with a deliberately narrow window.
5. From the final AppImage verify GitHub, Raise an Issue, About links and document hyperlinks open in the host environment.
6. Complete Print/PDF and drag/drop regression checks.
7. Only then promote 0.7.2 from stabilization candidate to canonical/release status.

## Stabilization candidate r2 — AppDir smoke shutdown regression

The r1 AppDir smoke reached and printed its success marker but the process remained alive until GNU `timeout` returned 124. This was a real QA-lifecycle defect: a passing assertion set is not sufficient if the packaged application cannot cleanly tear down the modeless Help/documentation windows and the temporary Retro/QScroller surface created by the smoke matrix.

r2 makes clean shutdown part of the smoke contract. In smoke mode Qt's implicit last-window quit policy is disabled, every retained dialog and Ricopad top-level window is explicitly closed, deferred deletions are drained, and the test fails if the application-level `OPEN_WINDOWS` registry is not empty. Only after that check does it print the success marker and call `app.exit(0)`. The builder still treats timeout 124 as a hard failure; no timeout is reclassified as success.

## Candidate r5.3 — save/reopen audit and correction

Date: 2026-09-15

The r5.3 audit reproduced the reported missing-space failure on PyQt 6.9.1, 6.10.2 and 6.11.0. A list marker set `after_list_marker` on its parent parser state, while a following RTF character group cloned and cleared only its child copy. Every sibling run could therefore trim its first literal space, and the stale parent state could reach a later non-list paragraph. LibreOffice opened the same Ricopad output with the spaces intact, isolating the defect to Ricopad's importer rather than its emitted text.

Review also confirmed that the UI's Indent/Outdent command wrote `QTextBlockFormat.indent()`, while the RTF serializer emitted only explicit margins and `QTextListFormat.indent()`. Normal indentation therefore reopened at zero, and list indentation did not create a real nested list level. The correction keeps scope paragraph-local: normal blocks receive equivalent serializable left-margin geometry; selected list blocks are moved to a copied semantic list format at levels 1–9, leaving unselected siblings untouched and reusing a compatible adjacent list on outdent.

The parser correction clears marker state before cloning a real following content group and at paragraph/table boundaries. Serializer fallback materialises any remaining generic block indentation, protecting programmatic or legacy live documents. The list importer stores level-0 geometry and reuses the parent list across nested runs, preventing both 360-twip-per-cycle drift and parent-list splitting. Regression coverage now includes a 20-fixture dependency-free corpus, normal/bold/italic list runs, a following normal paragraph, two save/reopen cycles, single/multi-paragraph list Indent/Outdent, and an actual blank first Save As → reopen → resave lifecycle.

The targeted Qt suite passes in the available environment under PyQt 6.9.1 / Qt 6.9.0, PyQt 6.10.2 / Qt 6.10.0 and PyQt 6.11.0 / Qt 6.11.0. LibreOffice also converts a generated mixed-format/nested r5.3 RTF with every tested space intact and four semantic list items. The full static/security/LibreOffice gate and final clean-extraction archive validation remain recorded by the r5.3 release procedure; target-built AppImage/touch/manual UI promotion checks are still mandatory for canonical release status.

## Candidate r5.4 — clean Untitled lifecycle audit and correction

Date: 2026-09-16

The startup audit confirmed that `build_ui()` connected `QTextDocument.modificationChanged` before `apply_preferences()` materialised the saved new-document defaults. `_apply_new_document_defaults_direct()` then called `document.clear()` and applied the first block format while `_loading` was false. Qt correctly emitted a modified state for those programmatic operations, and Ricopad incorrectly mirrored it into `content_saved=False`, producing `*Untitled.rtf` and an exit save prompt before any user edit.

File → New already used the correct ownership model: it bracketed the same formatting operations with `_loading=True`, explicitly reset the Qt modified flag, and left `content_saved=True`. r5.4 applies that established guard to constructor-time preference/default materialisation and restores both clean-state indicators before title/status initialization. Initial-file import still runs through the existing strict RTF loader. A failed import therefore keeps its error but now falls back to the already-clean, unbound Untitled document; zero-byte or malformed RTF input is not accepted, rewritten or claimed as open.

The live lifecycle gate now asserts immediate and post-event-loop clean startup, absence of a save question before editing, first-edit transition to modified state, the normal save question after editing, clean File → New reset, failed-import clean fallback, and blank Save As → reopen → resave. The complete Qt-backed RTF suite passes under PyQt 6.9.1 / Qt 6.9.0, PyQt 6.10.2 / Qt 6.10.0 and PyQt 6.11.0 / Qt 6.11.0. No RTF codec, editing command, interface, shortcut, theme, save or packaging code changed.
