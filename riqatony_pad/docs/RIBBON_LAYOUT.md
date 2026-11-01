# RiqatonyPad 1.1.2 Ribbon layout

Tabs: **File / Home / Insert / Configure / Help**. Home remains the default.

Every command button and compact selector is 52×52 px; Font Family is 104×52. Section captions remain below their controls. Expanded height is calculated from active style/content metrics.

## Home

- **Clipboard:** Select All, Cut, Delete, Paste Plain Text / Undo, Redo, Copy, Paste.
- **Font:** Font Face, Font Size, Font Style / Increase Font Size, Decrease Font Size, Font…, Text Colour.
- **Formatting:** Underline, Strikethrough, Subscript, Superscript / Bold, Italic, Highlight Colour, Bullet List.
- **Paragraph:** Align Right, Justify, Indent, Outdent / Align Left, Align Centre, Paragraph…, Line Spacing.

## Insert

- **Images & Links:** Edit Link, Remove Link / Image, Insert Link.
- **Tables:** Delete Table, Insert Column Left, Insert Column Right, Delete Column / Table, Insert Row Above, Insert Row Below, Delete Row.
- **Classics:** Date Only, Time Only, Clear Formatting / Date and Time, Horizontal Rule, Symbol.
- **Advanced:** Find, Find and Replace / Duplicate Line / Selection, Delete Line.

## Configure

- **View Control:** Full Screen, Show Status, Editor Layout / Zoom Out, Reset Zoom, Zoom In.
- **Editor Settings:** Editor Toolbar, Tab Width, New Document Defaults / Word Wrap, Dark Editor, Locked Mode.
- **Theme Settings:** Rico Icons Harmony, Rico Icons Classic, Rico Icons Legacy / Light, Dark, System.
- **App Settings:** Opens on New Window, Open Externally with Unsaved Changes / Opens on Active Window, Duplicate File with Unsaved Changes.

`Editor Layout`, `Editor Toolbar`, and the two dirty-state policy controls are menu-backed Ribbon selectors. Their icons come from the currently selected Rico family.

Ribbon pages retain horizontal scrolling/QScroller panning. Double-click a tab to collapse controls; click a tab title once to reveal them. Collapse state persists. Ribbon and Retro command tooltips display the shortcut owned by the shared QAction.
