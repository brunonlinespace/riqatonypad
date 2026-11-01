#!/usr/bin/env python3
"""Existing RiqatonyPad Ribbon and Retro presentation (x7.0 extraction only)."""
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFontComboBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMenu,
    QPushButton, QScrollArea, QScroller, QSizePolicy, QTabWidget,
    QToolButton, QVBoxLayout, QWidget,
)

RIBBON_BUTTON_SIZE = 52
RIBBON_ICON_SIZE = 36
RIBBON_FONT_FAMILY_WIDTH = RIBBON_BUTTON_SIZE * 2

class RibbonScrollArea(QScrollArea):
    """Horizontally pannable Ribbon surface without swallowing taps.

    QScroller owns the touch gesture arbitration: a finger drag scrolls after
    Qt's platform drag threshold, while a stationary tap is delivered to the
    child button/selector normally. Mouse wheel horizontal panning is retained.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        QScroller.grabGesture(
            self.viewport(), QScroller.ScrollerGestureType.TouchGesture
        )

    def pan_from_wheel_event(self, event):
        """Translate a wheel event into horizontal movement when possible."""
        bar = self.horizontalScrollBar()
        if bar.maximum() <= bar.minimum():
            return False
        pixel_delta = event.pixelDelta()
        angle_delta = event.angleDelta()
        delta = pixel_delta.y() or pixel_delta.x()
        if not delta:
            delta = angle_delta.y() or angle_delta.x()
            if delta:
                notches = int(delta / 120)
                if notches == 0:
                    notches = 1 if delta > 0 else -1
                delta = notches * max(48, bar.singleStep() * 3)
        if not delta:
            return False
        bar.setValue(bar.value() - int(delta))
        event.accept()
        return True

    def wheelEvent(self, event):
        if self.pan_from_wheel_event(event):
            return
        super().wheelEvent(event)


class EditorRibbonRetroMixin:

    def _attach_toolbar_context_menu(self, widget):
        """Expose the shared Ribbon/Retro switcher from a toolbar right-click."""
        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        widget.customContextMenuRequested.connect(
            lambda point, target=widget: self._show_toolbar_context_menu(target.mapToGlobal(point))
        )


    def _show_toolbar_context_menu(self, global_position):
        menu=QMenu(self)
        menu.addAction(self.layout_actions["ribbon"])
        menu.addAction(self.layout_actions["retro"])
        menu.addSeparator()
        menu.addAction(self.retro_toolbar_action)
        menu.exec(global_position)


    def build_ribbon(self):
        """Build the compact RTF-only Ribbon. Retro uses the same QAction commands."""
        self.app_menu_bar.setVisible(False); self.toolbar_stack.setVisible(False); self.main_layout.removeWidget(self.toolbar_stack)
        self.ribbon_tabs=QTabWidget(self.centralWidget()); self.ribbon_tabs.setObjectName("riqatonypadRibbon"); self.ribbon_tabs.setDocumentMode(True); self.ribbon_tabs.setMovable(False); self.ribbon_tabs.setTabsClosable(False)
        self.ribbon_tabs.tabBar().setExpanding(False); self.ribbon_tabs.tabBar().setUsesScrollButtons(True); self.ribbon_tabs.tabBar().installEventFilter(self)
        self.ribbon_tabs.installEventFilter(self)
        self._attach_toolbar_context_menu(self.ribbon_tabs)
        self._attach_toolbar_context_menu(self.ribbon_tabs.tabBar())
        self._ribbon_collapsed=False; self._ribbon_expanded_minimum_height=0; self._ribbon_expanded_maximum_height=0; self._interface_geometry_refresh_pending=False; self.ribbon_tabs.currentChanged.connect(self._sync_collapsed_ribbon_page)
        self.ribbon_buttons=[]; self.ribbon_sections=[]; self.ribbon_scroll_areas=[]; self.instant_tooltip_widgets=[]
        def instant(w): w.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips,True); w.setProperty("riqatonypad_instant_tooltip",True); w.installEventFilter(self); self.instant_tooltip_widgets.append(w); return w
        def page(label):
            scroll=RibbonScrollArea(self.ribbon_tabs); scroll.setObjectName(f"ribbon{label}Page"); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded); scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            body=QWidget(scroll); self._attach_toolbar_context_menu(scroll.viewport()); self._attach_toolbar_context_menu(body); row=QHBoxLayout(body); row.setContentsMargins(6,4,6,6); row.setSpacing(6); row.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop); scroll.setWidget(body); self.ribbon_tabs.addTab(scroll,label); self.ribbon_scroll_areas.append(scroll); scroll.horizontalScrollBar().rangeChanged.connect(lambda _minimum,_maximum:self._schedule_interface_geometry_refresh()); return row
        def group(layout,title):
            frame=QFrame(self.ribbon_tabs); frame.setObjectName("ribbonSection"); frame.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed); frame.setStyleSheet("QFrame#ribbonSection { background-color: palette(button); border: 1px solid palette(mid); border-radius: 6px;} QFrame#ribbonSection QLabel#ribbonSectionCaption {background:transparent;border:none;margin-bottom:2px;}")
            self.ribbon_sections.append(frame)
            outer=QVBoxLayout(frame); outer.setContentsMargins(8,5,8,6); outer.setSpacing(4); cap=QLabel(title,frame); cap.setObjectName("ribbonSectionCaption"); cap.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            cap_font=cap.font()
            if cap_font.pointSizeF()>0:
                cap_font.setPointSizeF(max(6.5,cap_font.pointSizeF()*0.74))
            elif cap_font.pixelSize()>0:
                cap_font.setPixelSize(max(8,int(round(cap_font.pixelSize()*0.74))))
            cap_font.setItalic(True)
            cap.setFont(cap_font)
            grid=QGridLayout(); grid.setContentsMargins(0,0,0,0); grid.setHorizontalSpacing(4); grid.setVerticalSpacing(3); outer.addLayout(grid); outer.addWidget(cap); layout.addWidget(frame); return frame,grid
        def normal(b): b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly); b.setIconSize(QSize(RIBBON_ICON_SIZE,RIBBON_ICON_SIZE)); b.setFixedSize(RIBBON_BUTTON_SIZE,RIBBON_BUTTON_SIZE); b.setFocusPolicy(Qt.FocusPolicy.NoFocus); instant(b); self._attach_toolbar_context_menu(b); return b
        def ab(grid,action,r,c,icon):
            b=QToolButton(self.ribbon_tabs); self.bind_custom_icon(action,icon)
            label=action.text().replace("&","").replace("…","").strip()
            tooltip=self._toolbar_action_tooltip(action,label)
            action.setToolTip(tooltip); b.setDefaultAction(action); b.setToolTip(tooltip); b.setAccessibleName(label)
            normal(b); grid.addWidget(b,r,c,Qt.AlignmentFlag.AlignCenter); self.ribbon_buttons.append(b); return b
        def fb(grid,w,r,c,icon,label,action):
            w.setParent(self.ribbon_tabs); w.setText("")
            clean=action.text().replace("&","").replace("…","").strip() or label
            tooltip=self._toolbar_action_tooltip(action,clean)
            action.setToolTip(tooltip); w.setToolTip(tooltip); w.setAccessibleName(clean)
            normal(w); self.bind_custom_icon(w,icon); grid.addWidget(w,r,c,Qt.AlignmentFlag.AlignCenter); self.ribbon_buttons.append(w); return w
        def mb(grid,menu,r,c,icon,label):
            b=QToolButton(self.ribbon_tabs); b.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup); b.setMenu(menu)
            b.setToolTip(label); b.setAccessibleName(label); normal(b); self.bind_custom_icon(b,icon)
            grid.addWidget(b,r,c,Qt.AlignmentFlag.AlignCenter); self.ribbon_buttons.append(b); return b
        def sel(grid,w,r,c,tip,width,span=1): w.setParent(self.ribbon_tabs); w.setToolTip(w.toolTip() or tip); w.setFixedSize(width,RIBBON_BUTTON_SIZE); w.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed); instant(w); grid.addWidget(w,r,c,1,span,Qt.AlignmentFlag.AlignCenter); return w
        # Resolve every Ribbon command through the same presentation-neutral
        # inventory used by Retro. The two interfaces may arrange controls
        # differently, but command identity, QAction/menu ownership and icon name
        # come from one authority.
        surface_specs={spec[1]:spec for spec in self.command_surface_catalog()}
        def spec(item_id,kind=None):
            value=surface_specs[item_id]
            if kind is not None and value[3] != kind:
                raise RuntimeError(f"Command surface kind mismatch for {item_id}: {value[3]} != {kind}")
            return value
        def cab(grid,item_id,r,c):
            _group,_id,_label,_kind,attr,icon=spec(item_id,"action")
            return ab(grid,getattr(self,attr),r,c,icon)
        def cfb(grid,w,item_id,r,c):
            _group,_id,label,_kind,attr,icon=spec(item_id,"action")
            return fb(grid,w,r,c,icon,label,getattr(self,attr))
        def cmb(grid,item_id,r,c):
            _group,_id,label,_kind,attr,icon=spec(item_id,"menu")
            return mb(grid,getattr(self,attr),r,c,icon,label)
        def csel(grid,w,item_id,r,c,width,span=1):
            _group,_id,label,kind,_attr,_icon=spec(item_id)
            if kind not in ("font-face","font-size","font-style","line-spacing"):
                raise RuntimeError(f"Command surface selector mismatch for {item_id}: {kind}")
            return sel(grid,w,r,c,label,width,span)

        file_page=page("File")
        _,g=group(file_page,"Create & Print")
        for item_id,r,c in (("print",0,0),("export-pdf",0,1),("page-setup",0,2),("new",1,0),("new-window",1,1),("open",1,2)): cab(g,item_id,r,c)
        _,g=group(file_page,"This File")
        for item_id,r,c in (("save-as",0,0),("properties",0,1),("delete-file",0,2),("external-editor",0,3),("save",1,0),("rename",1,1),("duplicate-file",1,2),("open-folder",1,3)): cab(g,item_id,r,c)
        _,g=group(file_page,"This Session"); cab(g,"save-exit",0,0); cab(g,"exit",1,0); file_page.addStretch(1)

        home=page("Home")
        _,g=group(home,"Clipboard")
        for item_id,r,c in (("select-all",0,0),("cut",0,1),("delete-text",0,2),("paste-plain",0,3),("undo",1,0),("redo",1,1),("copy",1,2),("paste",1,3)): cab(g,item_id,r,c)
        self.format_ribbon_group,g=group(home,"Font"); csel(g,self.font_combo,"font-face",0,0,RIBBON_FONT_FAMILY_WIDTH,2); csel(g,self.font_size_combo,"font-size",0,2,RIBBON_BUTTON_SIZE); csel(g,self.heading_combo,"font-style",0,3,RIBBON_BUTTON_SIZE); cab(g,"font-size-increase",1,0); cab(g,"font-size-decrease",1,1); cab(g,"font-dialog",1,2); cfb(g,self.text_colour_button,"text-color",1,3)
        _,g=group(home,"Formatting"); cfb(g,self.underline_button,"underline",0,0); cfb(g,self.strike_button,"strikethrough",0,1); cab(g,"subscript",0,2); cab(g,"superscript",0,3); cfb(g,self.bold_button,"bold",1,0); cfb(g,self.italic_button,"italic",1,1); cfb(g,self.highlight_button,"highlight",1,2); cfb(g,self.bullet_button,"bullet-list",1,3)
        self.paragraph_ribbon_group,g=group(home,"Paragraph"); cfb(g,self.align_right_button,"align-right",0,0); cfb(g,self.align_justify_button,"justify",0,1); cfb(g,self.indent_button,"indent",0,2); cfb(g,self.outdent_button,"outdent",0,3); cfb(g,self.align_left_button,"align-left",1,0); cfb(g,self.align_center_button,"align-center",1,1); cab(g,"paragraph",1,2); csel(g,self.line_spacing_combo,"line-spacing",1,3,RIBBON_BUTTON_SIZE)
        home.addStretch(1)

        insert_page=page("Insert")
        _,g=group(insert_page,"Images & Links"); cab(g,"edit-link",0,0); cab(g,"remove-link",0,1); cab(g,"insert-image",1,0); cab(g,"insert-link",1,1)
        _,g=group(insert_page,"Tables"); cab(g,"delete-table",0,0); cab(g,"insert-column-left",0,1); cab(g,"insert-column-right",0,2); cab(g,"delete-column",0,3); cab(g,"insert-table",1,0); cab(g,"insert-row-above",1,1); cab(g,"insert-row-below",1,2); cab(g,"delete-row",1,3)
        _,g=group(insert_page,"Classics"); cab(g,"insert-date",0,0); cab(g,"insert-time",0,1); cab(g,"clear-formatting",0,2); cab(g,"date-time",1,0); cab(g,"horizontal-rule",1,1); cab(g,"symbols",1,2)
        _,g=group(insert_page,"Advanced"); cab(g,"find",0,0); cab(g,"replace",0,1); cab(g,"duplicate-line",1,0); cab(g,"delete-line",1,1); insert_page.addStretch(1)

        view=page("Configure")
        _,g=group(view,"View Control"); cab(g,"full-screen",0,0); cab(g,"status-bar",0,1); cmb(g,"editor-layout",0,2); cab(g,"zoom-out",1,0); cab(g,"zoom-reset",1,1); cab(g,"zoom-in",1,2)
        _,g=group(view,"Editor Settings"); cmb(g,"editor-toolbar",0,0); cab(g,"tab-width",0,1); cab(g,"default-font",0,2); cab(g,"word-wrap",1,0); cab(g,"editor-canvas",1,1); cab(g,"view-only",1,2)
        _,g=group(view,"Theme Settings"); cab(g,"icons-new",0,0); cab(g,"icons-classic",0,1); cab(g,"icons-original",0,2); cab(g,"theme-light",1,0); cab(g,"theme-dark",1,1); cab(g,"theme-system",1,2)
        _,g=group(view,"App Settings"); cab(g,"drop-new-window",0,0); cmb(g,"dirty-external",0,1); cab(g,"drop-active",1,0); cmb(g,"dirty-duplicate",1,1); view.addStretch(1)

        # AppMenu selector icons also resolve through the shared inventory.
        for item_id in ("editor-layout","editor-toolbar","app-theme","app-icons","app-drag-drop","dirty-duplicate","dirty-external"):
            _group,_id,_label,_kind,attr,icon=spec(item_id,"menu")
            self.bind_custom_icon(getattr(self,attr).menuAction(),icon)

        help_page=page("Help"); _,g=group(help_page,"Help"); cab(g,"documentation",0,0); cab(g,"tutorial",0,1); cab(g,"shortcuts",1,0); cab(g,"about",1,1); _,g=group(help_page,"GitHub"); cab(g,"github",0,0); cab(g,"issue",1,0); help_page.addStretch(1)
        self.search_container.setParent(self.centralWidget()); self.search_container.setObjectName("ribbonSearchBar"); self.main_layout.insertWidget(0,self.ribbon_tabs); self.main_layout.addWidget(self.search_container); self.search_container.setVisible(self.show_search_bar); self.ribbon_tabs.setCurrentIndex(1)
        self.next_ribbon_tab_action=QAction("Next Ribbon Tab",self); self.next_ribbon_tab_action.setShortcut(QKeySequence("Ctrl+Tab")); self.next_ribbon_tab_action.triggered.connect(lambda:self.cycle_ribbon_tab(1)); self.addAction(self.next_ribbon_tab_action)
        self.previous_ribbon_tab_action=QAction("Previous Ribbon Tab",self); self.previous_ribbon_tab_action.setShortcut(QKeySequence("Ctrl+Shift+Tab")); self.previous_ribbon_tab_action.triggered.connect(lambda:self.cycle_ribbon_tab(-1)); self.addAction(self.previous_ribbon_tab_action)
        self.format_toolbar.setVisible(False); self.menu_buttons_container.setVisible(False); self.toolbar.setVisible(False)
        QTimer.singleShot(0,self._refresh_interface_geometry)


    def _toolbar_action_tooltip(self, action, label=None):
        """Return the authoritative icon-toolbar tooltip for one QAction."""
        explicit=action.property("riqatonypad_toolbar_tooltip")
        if explicit:
            clean=str(explicit).replace("&","").strip()
        else:
            clean=(label or action.text() or "").replace("&","").replace("…","").strip()
        shortcut=action.shortcut().toString(QKeySequence.SequenceFormat.NativeText).strip()
        return f"{clean} — {shortcut}" if shortcut else clean


    def _normalise_retro_button(self, button, label, tooltip=None):
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        button.setIconSize(QSize(RIBBON_ICON_SIZE, RIBBON_ICON_SIZE))
        button.setFixedSize(RIBBON_BUTTON_SIZE, RIBBON_BUTTON_SIZE)
        button.setAutoRaise(False)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setAccessibleName(label)
        if tooltip:
            button.setToolTip(tooltip)
        button.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        self._attach_toolbar_context_menu(button)
        return button


    def _retro_selector(self, kind):
        if kind == "font-face":
            widget = QFontComboBox(self.retro_toolbar_body)
            widget.setEditable(True)
            widget.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            widget.setFixedSize(RIBBON_FONT_FAMILY_WIDTH, RIBBON_BUTTON_SIZE)
            line_edit = widget.lineEdit()
            if line_edit is not None:
                line_edit.setReadOnly(True)
                line_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                line_edit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            widget.setToolTip("Font Face")
            widget.currentFontChanged.connect(self.set_selected_font)
            return widget
        if kind == "font-size":
            widget = QComboBox(self.retro_toolbar_body)
            widget.setEditable(True)
            widget.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            widget.addItems(["8", "9", "10", "11", "12", "14", "16", "18", "20", "24", "28", "32", "36", "48", "72"])
            widget.setFixedSize(RIBBON_BUTTON_SIZE, RIBBON_BUTTON_SIZE)
            widget.setToolTip("Font Size")
            widget.currentTextChanged.connect(self.set_selected_font_size)
            return widget
        if kind == "font-style":
            widget = QComboBox(self.retro_toolbar_body)
            for text, level in (("Normal", 0), ("Heading 1", 1), ("Heading 2", 2), ("Heading 3", 3), ("Heading 4", 4), ("Heading 5", 5), ("Heading 6", 6)):
                widget.addItem(text, level)
            widget.setFixedSize(RIBBON_BUTTON_SIZE, RIBBON_BUTTON_SIZE)
            widget.setToolTip("Font Style — Normal Ctrl+Shift+0; Headings 1–6 Ctrl+Shift+1…6")
            widget.currentIndexChanged.connect(lambda _index, combo=widget: self.apply_heading(int(combo.currentData() or 0)))
            return widget
        if kind == "line-spacing":
            widget = QComboBox(self.retro_toolbar_body)
            for label, value in (("1", 100), ("1.15", 115), ("1.5", 150), ("2", 200)):
                widget.addItem(label, value)
            widget.setFixedSize(RIBBON_BUTTON_SIZE, RIBBON_BUTTON_SIZE)
            widget.setToolTip("Line Spacing — 1.0 Ctrl+1; 1.15 Ctrl+2; 1.5 Ctrl+3; 2.0 Ctrl+4")
            widget.currentIndexChanged.connect(lambda _index, combo=widget: self.set_line_spacing(int(combo.currentData() or 100)))
            return widget
        return None


    def build_retro_toolbar(self):
        """Build Retro as one horizontally scrollable 52px command row.

        Deliberately do not use QToolBar: Qt's private extension button has
        platform/style-dependent geometry and repeatedly produced an overflow
        arrow that did not match RiqatonyPad.  Retro now uses the same QScroller
        touch arbitration and wheel panning model as Ribbon.
        """
        self.retro_toolbar=RibbonScrollArea(self.centralWidget())
        self.retro_toolbar.setObjectName("riqatonypadRetroToolbar")
        self.retro_toolbar.setWidgetResizable(False)
        self.retro_toolbar.setFrameShape(QFrame.Shape.NoFrame)
        self.retro_toolbar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.retro_toolbar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.retro_toolbar.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)
        self.retro_toolbar.installEventFilter(self)
        self._attach_toolbar_context_menu(self.retro_toolbar)
        self._attach_toolbar_context_menu(self.retro_toolbar.viewport())
        self.retro_toolbar.horizontalScrollBar().rangeChanged.connect(lambda _minimum,_maximum:self._schedule_interface_geometry_refresh())
        self.retro_toolbar_body=QWidget(self.retro_toolbar)
        self._attach_toolbar_context_menu(self.retro_toolbar_body)
        self.retro_toolbar_body.setObjectName("riqatonypadRetroToolbarBody")
        self.retro_toolbar_layout=QHBoxLayout(self.retro_toolbar_body)
        self.retro_toolbar_layout.setContentsMargins(4,4,4,4)
        self.retro_toolbar_layout.setSpacing(3)
        self.retro_toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.retro_toolbar.setWidget(self.retro_toolbar_body)
        self.main_layout.insertWidget(0,self.retro_toolbar)
        self.retro_toolbar.setVisible(False)
        self.retro_toolbar_widgets=[]
        self.retro_selector_widgets=[]
        self.retro_format_widgets=[]
        self.retro_icon_bindings=[]
        self.rebuild_retro_toolbar()


    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            child = item.layout()
            if child is not None:
                self._clear_layout(child)


    def rebuild_retro_toolbar(self):
        if not hasattr(self,"retro_toolbar"):
            return
        self._clear_layout(self.retro_toolbar_layout)
        self.retro_toolbar_widgets=[]; self.retro_selector_widgets=[]; self.retro_format_widgets=[]; self.retro_icon_bindings=[]; self.retro_symbols_button=None
        catalog={item[1]:item for item in self.retro_toolbar_catalog()}
        for _group,_id,_label,kind,attr,icon in catalog.values():
            if kind=="action" and attr and icon:
                action=getattr(self,attr,None)
                if action is not None:
                    action.setIcon(self.custom_icon(icon)); self.retro_icon_bindings.append((action,icon))
        formatting={"Font","Formatting","Paragraph","Insert"}
        for item_id in self.retro_toolbar_items:
            spec=catalog.get(item_id)
            if not spec:
                continue
            group,_id,label,kind,attr,icon=spec
            if kind in ("font-face","font-size","font-style","line-spacing"):
                widget=self._retro_selector(kind)
                if widget is None:
                    continue
                self.retro_toolbar_layout.addWidget(widget)
                self.retro_toolbar_widgets.append(widget)
                self.retro_selector_widgets.append(widget)
                if group in formatting:
                    self.retro_format_widgets.append(widget)
                continue
            if kind == "menu":
                menu=getattr(self,attr,None)
                if menu is None:
                    continue
                button=QToolButton(self.retro_toolbar_body)
                button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
                button.setMenu(menu)
                self._normalise_retro_button(button,label,label)
                button.setIcon(self.custom_icon(icon)); self.retro_icon_bindings.append((button,icon))
                button.setProperty("riqatonypad_instant_tooltip",True)
                button.installEventFilter(self)
                self.retro_toolbar_layout.addWidget(button)
                self.retro_toolbar_widgets.append(button)
                continue
            action=getattr(self,attr,None)
            if action is None:
                continue
            button=QToolButton(self.retro_toolbar_body)
            clean=action.text().replace("&","").replace("…","").strip() or label
            tooltip=self._toolbar_action_tooltip(action,clean)
            action.setToolTip(tooltip); button.setDefaultAction(action); button.setToolTip(tooltip)
            self._normalise_retro_button(button,clean,tooltip)
            button.setProperty("riqatonypad_instant_tooltip",True)
            button.installEventFilter(self)
            self.retro_toolbar_layout.addWidget(button)
            if item_id=="symbols":
                self.retro_symbols_button=button
            self.retro_toolbar_widgets.append(button)
        self.retro_toolbar_layout.activate()
        self.retro_toolbar_body.adjustSize()
        QTimer.singleShot(0, self._refresh_interface_geometry)
        self.update_formatting_state(); self._update_mode_capabilities()


    def refresh_interface_theme(self):
        """Re-polish persistent Ribbon/Retro surfaces after an app palette change.

        Rico Plus established this contract for its persistent Ribbon: Qt style-sheet
        palette roles can retain their previous polish after QApplication changes
        palette. RiqatonyPad uses the same treatment for its Ribbon and its alternative
        Retro command surface, without touching the independently themed editor
        canvas.
        """
        for frame in tuple(getattr(self,"ribbon_sections",())):
            try:
                sheet=frame.styleSheet()
                frame.setStyleSheet("")
                frame.setStyleSheet(sheet)
            except RuntimeError:
                continue
        widgets=[]
        for root in (
            getattr(self,"ribbon_tabs",None),
            getattr(self,"retro_toolbar",None),
            getattr(self,"toolbar_stack",None),
        ):
            if isinstance(root,QWidget):
                widgets.extend((root,*root.findChildren(QWidget)))
        seen=set()
        for widget in widgets:
            ident=id(widget)
            if ident in seen:
                continue
            seen.add(ident)
            try:
                style=widget.style()
                style.unpolish(widget)
                style.polish(widget)
                widget.update()
            except RuntimeError:
                continue


    def _schedule_interface_geometry_refresh(self):
        """Coalesce style/layout changes into one square-control geometry pass."""
        if getattr(self,"_interface_geometry_refresh_pending",False):
            return
        self._interface_geometry_refresh_pending=True
        QTimer.singleShot(0,self._refresh_interface_geometry)


    def _refresh_ribbon_geometry(self):
        """Derive expanded Ribbon height from its real 52px controls and active Qt style."""
        tabs=getattr(self,"ribbon_tabs",None)
        if tabs is None:
            return
        max_body_height=0
        for frame in getattr(self,"ribbon_sections",()):
            layout=frame.layout()
            if layout is not None:
                layout.activate()
            hint=frame.sizeHint()
            frame.setFixedHeight(max(1,hint.height()))
        page_heights=[]
        for scroll in getattr(self,"ribbon_scroll_areas",()):
            body=scroll.widget()
            if body is None:
                continue
            layout=body.layout()
            if layout is not None:
                layout.activate()
            body_height=max(body.minimumSizeHint().height(),body.sizeHint().height())
            max_body_height=max(max_body_height,body_height)
            # Reserve the native horizontal-scrollbar extent even before it is
            # needed. This prevents a narrow window/theme change from stealing
            # vertical space from the two fixed 52px control rows.
            hbar=scroll.horizontalScrollBar()
            scrollbar_height=max(hbar.minimumSizeHint().height(),hbar.sizeHint().height())
            page_heights.append(body_height+scrollbar_height+(scroll.frameWidth()*2))
        if not page_heights:
            return
        page_height=max(page_heights)
        for scroll in self.ribbon_scroll_areas:
            scroll.setFixedHeight(page_height)
        tabs.tabBar().ensurePolished()
        tab_height=max(tabs.tabBar().minimumSizeHint().height(),tabs.tabBar().sizeHint().height())
        # The small two-pixel pane allowance covers native/Fusion tab-pane
        # borders without guessing a fixed full Ribbon height.
        expanded_height=tab_height+page_height+2
        self._ribbon_expanded_minimum_height=expanded_height
        self._ribbon_expanded_maximum_height=expanded_height
        if not getattr(self,"_ribbon_collapsed",False):
            tabs.setFixedHeight(expanded_height)
        tabs.updateGeometry()


    def _refresh_retro_geometry(self):
        """Keep Retro on one exact 52px row with scroll overflow only."""
        toolbar=getattr(self,"retro_toolbar",None)
        body=getattr(self,"retro_toolbar_body",None)
        layout=getattr(self,"retro_toolbar_layout",None)
        if toolbar is None or body is None or layout is None:
            return
        for widget in getattr(self,"retro_toolbar_widgets",()):
            if isinstance(widget,QFontComboBox):
                widget.setFixedSize(RIBBON_FONT_FAMILY_WIDTH,RIBBON_BUTTON_SIZE)
            else:
                widget.setFixedSize(RIBBON_BUTTON_SIZE,RIBBON_BUTTON_SIZE)
            widget.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        layout.activate()
        hint=layout.sizeHint()
        margins=layout.contentsMargins()
        body_height=RIBBON_BUTTON_SIZE+margins.top()+margins.bottom()
        body_width=max(hint.width(),margins.left()+margins.right()+1)
        body.setFixedSize(body_width,body_height)
        # Reserve only the real horizontal scrollbar when content overflows.
        # There is no QToolBar extension control and therefore no overflow arrow.
        viewport_width=max(1,toolbar.viewport().width())
        scrollbar_height=toolbar.horizontalScrollBar().sizeHint().height() if body_width>viewport_width else 0
        toolbar.setFixedHeight(body_height+scrollbar_height)
        toolbar.updateGeometry()


    def _refresh_interface_geometry(self):
        """Enforce one 52px control grid across Ribbon/Retro and every AppImage theme."""
        self._interface_geometry_refresh_pending=False
        for button in getattr(self,"ribbon_buttons",()):
            button.setFixedSize(RIBBON_BUTTON_SIZE,RIBBON_BUTTON_SIZE)
            button.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        ribbon_selectors=(
            (getattr(self,"font_combo",None),RIBBON_FONT_FAMILY_WIDTH),
            (getattr(self,"font_size_combo",None),RIBBON_BUTTON_SIZE),
            (getattr(self,"heading_combo",None),RIBBON_BUTTON_SIZE),
            (getattr(self,"line_spacing_combo",None),RIBBON_BUTTON_SIZE),
        )
        for widget,width in ribbon_selectors:
            if widget is not None:
                widget.setFixedSize(width,RIBBON_BUTTON_SIZE)
                widget.setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self._refresh_ribbon_geometry()
        self._refresh_retro_geometry()


    def _sync_retro_selectors(self, fmt, block):
        if not hasattr(self, "retro_toolbar_widgets"):
            return
        for widget in self.retro_toolbar_widgets:
            widget.blockSignals(True)
        try:
            for widget in self.retro_toolbar_widgets:
                tip = widget.toolTip()
                if isinstance(widget, QFontComboBox) and tip == "Font Face":
                    widget.setCurrentFont(fmt.font())
                    line_edit = widget.lineEdit()
                    if line_edit is not None:
                        line_edit.setCursorPosition(0)
                elif isinstance(widget, QComboBox) and tip == "Font Size":
                    widget.setEditText(f"{self._logical_char_size(fmt):g}")
                elif isinstance(widget, QComboBox) and tip == "Font Style":
                    level = block.headingLevel() if hasattr(block, "headingLevel") else 0
                    widget.setCurrentIndex(max(0, widget.findData(level)))
                elif isinstance(widget, QComboBox) and tip == "Line Spacing":
                    line_height = round(block.lineHeight()) if block.lineHeight() else 100
                    idx = min(range(widget.count()), key=lambda i: abs(int(widget.itemData(i)) - line_height))
                    widget.setCurrentIndex(idx)
        finally:
            for widget in self.retro_toolbar_widgets:
                widget.blockSignals(False)


    def set_workspace_layout(self, mode):
        """Arrange interface and Find bar without recreating document widgets."""
        try: mode=int(mode)
        except (TypeError,ValueError): return
        if mode not in (1,2,3,4): return
        self.workspace_layout=mode
        for value,action in getattr(self,"workspace_layout_actions",{}).items():
            action.blockSignals(True); action.setChecked(value==mode); action.blockSignals(False)
        self.apply_workspace_layout(); self.save_preferences()


    def apply_workspace_layout(self):
        if not all(hasattr(self,name) for name in ("ribbon_tabs","retro_toolbar","search_container","external_banner","visual_editor")):
            return
        widgets=(self.ribbon_tabs,self.retro_toolbar,self.search_container,self.external_banner,self.visual_editor)
        for widget in widgets: self.main_layout.removeWidget(widget)
        interface=(self.retro_toolbar if self.interface_style=="retro" else self.ribbon_tabs)
        inactive=(self.ribbon_tabs if self.interface_style=="retro" else self.retro_toolbar)
        inactive.setVisible(False); interface.setVisible(True)

        def add_editor_block():
            # Keep the external-change warning structurally attached to the editor,
            # matching Rico Plus regardless of where the standalone toolbar/search
            # surfaces are arranged.
            self.main_layout.addWidget(self.external_banner)
            self.main_layout.addWidget(self.visual_editor,1)

        if self.workspace_layout==1:
            self.main_layout.addWidget(interface); self.main_layout.addWidget(self.search_container); add_editor_block()
        elif self.workspace_layout==2:
            add_editor_block(); self.main_layout.addWidget(self.search_container); self.main_layout.addWidget(interface)
        elif self.workspace_layout==3:
            self.main_layout.addWidget(interface); add_editor_block(); self.main_layout.addWidget(self.search_container)
        else:
            self.main_layout.addWidget(self.search_container); add_editor_block(); self.main_layout.addWidget(interface)
        self.search_container.setVisible(self.show_search_bar)
        self.external_banner.setVisible(bool(self._external_change_pending))


    def set_interface_style(self, style, persist=True):
        """Switch between Ribbon and Retro without moving the Find bar."""
        style = str(style).lower()
        if style not in ("ribbon", "retro"):
            style = "ribbon"
        self.interface_style = style
        is_retro = style == "retro"
        if hasattr(self, "ribbon_tabs"):
            self.ribbon_tabs.setVisible(not is_retro)
        if hasattr(self, "retro_toolbar"):
            self.retro_toolbar.setVisible(is_retro)
        if hasattr(self, "app_menu_bar"):
            # Retro participates in the platform-native menu system. On Plasma
            # this allows Menu Only / Global Menu to export the menu normally.
            self.app_menu_bar.setNativeMenuBar(True)
            self.app_menu_bar.setVisible(is_retro)
        for mode, action in getattr(self, "layout_actions", {}).items():
            action.blockSignals(True)
            action.setChecked(mode == style)
            action.blockSignals(False)
        if hasattr(self,"visual_editor") and hasattr(self,"search_container"):
            self.apply_workspace_layout()
        if persist:
            self.save_preferences()
        self._show_status_message(
            "Retro interface enabled." if is_retro else "Ribbon interface enabled.", 2000
        )


    def show_retro_toolbar_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Customise Retro Bar — RiqatonyPad")
        dialog.resize(560, 620)
        outer = QVBoxLayout(dialog)
        intro = QLabel(
            "Tick the controls you want on the Retro bar. All commands remain "
            "available from the application menus regardless of toolbar selection.",
            dialog,
        )
        intro.setWordWrap(True)
        outer.addWidget(intro)
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        body = QWidget(scroll)
        body_layout = QVBoxLayout(body)
        checks = {}
        current_group = None
        group_layout = None
        for group, item_id, label, _kind, _attr, _icon in self.retro_toolbar_catalog():
            if group != current_group:
                box = QGroupBox(group, body)
                group_layout = QVBoxLayout(box)
                body_layout.addWidget(box)
                current_group = group
            check = QCheckBox(label, body)
            check.setChecked(item_id in self.retro_toolbar_items)
            group_layout.addWidget(check)
            checks[item_id] = check
        body_layout.addStretch(1)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)
        controls = QHBoxLayout()
        default_button = QPushButton("Default", dialog)
        controls.addWidget(default_button)
        controls.addStretch(1)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        controls.addWidget(buttons)
        outer.addLayout(controls)

        def restore_default():
            defaults = set(RETRO_TOOLBAR_DEFAULT)
            for item_id, check in checks.items():
                check.setChecked(item_id in defaults)

        def save_selection():
            self.retro_toolbar_items = [
                item[1] for item in self.retro_toolbar_catalog()
                if checks[item[1]].isChecked()
            ]
            self.rebuild_retro_toolbar()
            self.save_preferences()
            dialog.accept()

        default_button.clicked.connect(restore_default)
        buttons.accepted.connect(save_selection)
        buttons.rejected.connect(dialog.reject)
        dialog.exec()


    def cycle_ribbon_tab(self, direction):
        """Move to the next/previous visible ribbon tab with wrap-around."""
        count = self.ribbon_tabs.count()
        if count <= 0:
            return
        current = self.ribbon_tabs.currentIndex()
        self.ribbon_tabs.setCurrentIndex((current + int(direction)) % count)


    def _collapsed_ribbon_height(self):
        """Return enough height for the tab titles while hiding page contents."""
        tab_bar = self.ribbon_tabs.tabBar()
        return max(tab_bar.height(), tab_bar.sizeHint().height(), 1) + 2


    def _sync_collapsed_ribbon_page(self, _index=None):
        """Keep page contents hidden when tabs are changed while collapsed."""
        if not getattr(self, "_ribbon_collapsed", False):
            return
        current = self.ribbon_tabs.currentWidget()
        if current is not None:
            current.setVisible(False)


    def set_ribbon_collapsed(self, collapsed, *, persist=True):
        collapsed=bool(collapsed)
        if persist:
            self.ribbon_collapsed_preference = collapsed
        if collapsed == getattr(self,"_ribbon_collapsed",False):
            if persist: self.save_preferences()
            return
        self._ribbon_collapsed=collapsed
        current=self.ribbon_tabs.currentWidget()
        if collapsed:
            if current is not None: current.setVisible(False)
            height=self._collapsed_ribbon_height(); self.ribbon_tabs.setMinimumHeight(height); self.ribbon_tabs.setMaximumHeight(height)
            self._show_status_message("Ribbon controls hidden. Click a tab title once to reveal them.",3000)
        else:
            self.ribbon_tabs.setFixedHeight(self._ribbon_expanded_minimum_height)
            if current is not None: current.setVisible(True)
            self._show_status_message("Ribbon controls revealed.",2000)
        self.ribbon_tabs.updateGeometry()
        if persist: self.save_preferences()


    def toggle_ribbon_collapsed(self):
        """Toggle ribbon visibility without hiding the tab titles."""
        self.set_ribbon_collapsed(not getattr(self, "_ribbon_collapsed", False))

