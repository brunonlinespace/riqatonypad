# Ricopad 1.0.15 — App Drag-and-Drop parent icon synchronization

Ricopad 1.0.15 is deliberately limited to synchronizing the AppMenu **App Drag-and-Drop** parent icon with its currently selected radio option.

- **Opens on Active Window** makes the parent use the same `drop-active` icon.
- **Opens on New Window** makes the parent use the same `drop-new-window` icon.
- The parent icon updates after preference application, a drag/drop-mode change, and theme/icon-family refresh.
- The existing radio actions remain the sole authority for drag/drop behavior and persistence.

No drag/drop behavior, RTF codec/serializer, rich-text support, document-format, file-lifecycle, Quick Tour, shortcut, layout, theme semantics, or unrelated logic changes are included.

No RTF codec/serializer, rich-text support, document-format, or file-lifecycle logic changes are included.
