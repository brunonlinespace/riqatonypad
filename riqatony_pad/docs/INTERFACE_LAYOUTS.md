# RiqatonyPad 1.1.2 interfaces and layouts

## View AppMenu

Current order:

1. Full Screen
2. Show Status
3. separator
4. Word Wrap
5. Dark Editor
6. separator
7. Locked Mode
8. Editor Layout → Toolbar Top / Find Bottom / Toolbar Top / Find Top / Toolbar Bottom / Find Top / Toolbar Bottom / Find Bottom
9. Editor Toolbar → Ribbon (default) / Retro / separator / Customise Retro Bar…
10. separator
11. Editor Zoom → Zoom In / Zoom Out / separator / Reset Zoom
12. Editor Miscellaneous → Tab Width… / New Document Defaults…

`Editor Layout` uses the family-relative `launch-dashboard` icon and `Editor Toolbar` uses `layout-ribbon`. Their submenu entries intentionally have no icons.

## Settings AppMenu

1. App Theme → Light / Dark / System
2. App Icons → Riqa Icons Harmony / Riqa Icons Humility / Riqa Icons Heritage
3. App Drag-and-Drop → Opens on Active Window / Opens on New Window
4. separator
5. Duplicate File with Unsaved Changes → Ask Every Time / Duplicate Current Document / Duplicate Last Saved Version
6. Open Externally with Unsaved Changes → Ask Every Time / Save Changes and Open / Open Last Saved Version

App Theme, App Icons and App Drag-and-Drop retain icons inside their submenus. The two dirty-state policy submenus intentionally do not.

## Configure Ribbon

- **View Control** — Full Screen / Show Status / Editor Layout; Zoom Out / Reset Zoom / Zoom In.
- **Editor Settings** — Editor Toolbar / Tab Width / New Document Defaults; Word Wrap / Dark Editor / Locked Mode.
- **Theme Settings** — Riqa Icons Harmony / Riqa Icons Humility / Riqa Icons Heritage; Light / Dark / System.
- **App Settings** — Opens on New Window / Open Externally with Unsaved Changes; Opens on Active Window / Duplicate File with Unsaved Changes.

Ribbon pages remain horizontally scrollable/QScroller-enabled. Ribbon and Retro share the same actions and shortcuts.

## Retro Bar

Retro uses the same `COMMAND_SURFACE_SPECS` inventory as Ribbon. **Customise Retro Bar…** exposes every applicable action, selector and menu-backed control from that shared inventory; the two interfaces differ only in presentation and chosen layout. Menu-backed controls open the same menus used by Ribbon/AppMenu, so checked state and preferences cannot drift between surfaces.

Default Retro row:

1. New
2. Open
3. Save
4. Undo
5. Redo
6. Font Face
7. Font Size
8. Bold
9. Italic
10. Underline
11. Highlight
12. Text Colour
13. Bullet List
14. Align Left
15. Align Centre
16. Indent
17. Image
18. Table
19. Find and Replace

The full customizer is grouped as File, Clipboard, Font, Formatting, Paragraph, Insert, Advanced, View Control, Editor Settings, Theme Settings, App Settings and Help.

## Editor Layout shortcut order (1.0.11)

1. **Toolbar Top / Find Bottom** — `Ctrl+Alt+Shift+1` — default when no saved layout exists
2. **Toolbar Top / Find Top** — `Ctrl+Alt+Shift+2`
3. **Toolbar Bottom / Find Top** — `Ctrl+Alt+Shift+3`
4. **Toolbar Bottom / Find Bottom** — `Ctrl+Alt+Shift+4`

Existing saved numeric layout values retain their existing physical arrangement; 1.0.11 changes menu order/labels/shortcuts and the unsaved default, not the layout engine.
