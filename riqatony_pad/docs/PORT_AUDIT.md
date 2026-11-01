# Ricopad implementation audit record

0.8.0-r3 preserves the reviewed 0.7.3-exp1-r2 implementation unchanged; the release scope is portable/AppImage packaging normalization.

## Source baseline

0.7.2 is patched from the exact 0.7.1 canonical source tree and preserves the two-item outer layout plus RTF-only scope.

## Interoperable list rewrite

The old output path could represent lists with marker-oriented paragraph controls that Ricopad understood but external applications did not consistently recognise as semantic lists. 0.7.2 moves canonical output to standard RTF `listtable`/`listoverridetable` structures and `ls`/`ilvl` paragraph references. LibreOffice headless conversion is a release QA input rather than an assumption.

## Paragraph state isolation

Selection-wide paragraph commands were reviewed for accidental reuse of one block's complete format. Alignment, indentation, line spacing and Paragraph dialog writes now mutate a copy of each target block's own format. List identity therefore remains owned by the original block/list object.

## New-document defaults

The generated template remains for deterministic representation, but the new-document path now materialises defaults directly into QTextDocument. This removes an unnecessary serialize/import normalization boundary from the user's first blank document.

## Retro overflow

The Qt private toolbar-extension geometry path is removed. Retro is now the same class of horizontally pannable surface as Ribbon, with no private extension button dependency.

## Host links

Host opening strips AppImage/frozen Qt/library environment variables before invoking system openers. QDesktopServices remains only a fallback.

## Review outcome

See `CODE_REVIEW_0.7.2.md` for the separate after-fix review and remaining live release gates.
