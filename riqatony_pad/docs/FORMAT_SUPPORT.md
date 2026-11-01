# RTF format support in RiqatonyPad 1.1.2

RiqatonyPad 1.1.2 retains the 1.0.1 RTF implementation unchanged. The supported interoperable subset and loss-warning boundaries below remain authoritative.

RiqatonyPad opens and saves `.rtf` only. The 0.7.2 line treats standards interoperability as the persistence target.

## Supported core

- Unicode text and common RTF code-page escapes
- font family and point size, including supported stylesheet inheritance
- bold, italic, underline, strikethrough, superscript and subscript
- explicit foreground colour and highlight/background colour
- automatic/unset foreground and no-highlight as distinct states
- paragraph alignment, margins/indentation, before/after spacing and line spacing
- tabs and manual line breaks
- standard bullet lists; externally imported standard decimal lists are retained as an interoperability-only case
- safe hyperlinks
- embedded PNG/JPEG images
- horizontal rules
- bounded non-nested tables (maximum 1,000 rows, 64 columns, 20,000 cells) with supported simple geometry
- safe page size/margins/landscape properties

## List interoperability

RiqatonyPad-created bullet lists use the RTF 1.9.x list model: `listtable`, `listlevel`, `listid`, `listoverridetable`, `ls` and `ilvl`, so external applications such as LibreOffice recognise them as semantic bullets rather than marker text. Numbered-list creation is deliberately absent from the current UI. Decimal list parsing/serialization remains only so standards-based numbered lists already present in external RTF files are not needlessly flattened during a supported round-trip.

## Automatic colour and highlights

An unset/automatic foreground remains automatic in saved RTF. When a highlight would make automatic text unreadable on the RiqatonyPad canvas, RiqatonyPad may use a temporary black/white display foreground tagged as automatic; the serializer deliberately does not emit that display aid as an explicit `cf` colour.

## Portability rules

Images are embedded in RTF output. Explicit user hyperlinks are retained only for safe schemes/relative targets. AppImage link activation uses the cleaned host environment so the system browser/file manager is not asked to run inside the AppImage Qt/library environment.

## Unsupported/partial constructs

RiqatonyPad does not promise lossless editing of OLE/object payloads, shapes/drawing objects, headers/footers, comments/annotations, footnotes/endnotes, tracked revisions, nested tables, complex bidirectional paragraph controls, advanced tab leaders, or every producer-specific RTF extension. Properties/pre-save warnings identify known unsupported constructs before a dirty rewrite.
