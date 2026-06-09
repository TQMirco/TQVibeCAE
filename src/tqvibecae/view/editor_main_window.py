"""Finestra principale editor schematico"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QWidget

from tqvibecae.model.presentation import WireKind
from tqvibecae.view.editor_docks import build_editor_docks
from tqvibecae.view.editor_menus import build_editor_menus
from tqvibecae.view.editor_toolbars import build_editor_toolbars
from tqvibecae.view.messages_panel import MessagesPanel
from tqvibecae.view.navigator_panel import NavigatorPanel
from tqvibecae.view.properties_panel import PropertiesPanel
from tqvibecae.view.schematic_canvas import SchematicCanvasView
from tqvibecae.view.status_bar import EditorStatusBar
from tqvibecae.view.symbol_palette import SymbolPaletteView
from tqvibecae.view.toolbox_bar import ToolboxBar
from tqvibecae.viewmodel.schematic_editor_vm import SchematicEditorViewModel, ToolMode


class SchematicEditorWindow(QMainWindow):
    """Shell CAD con dock, menu, toolbox e canvas centrale."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TQVibeCAE — Editor schematico")
        self.resize(1400, 900)

        self._viewmodel = SchematicEditorViewModel(self)
        self._navigator = NavigatorPanel(self)
        self._palette = SymbolPaletteView(self)
        self._palette.load_catalog(self._viewmodel.catalog)
        self._properties = PropertiesPanel(self)
        self._messages = MessagesPanel(self)
        self._toolbox = ToolboxBar(self)
        self._canvas = SchematicCanvasView(self)

        central = QWidget(self)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._toolbox)
        layout.addWidget(self._canvas, stretch=1)
        self.setCentralWidget(central)

        self._docks = build_editor_docks(
            self,
            self._navigator,
            self._palette,
            self._properties,
            self._messages,
        )
        self._toolbars = build_editor_toolbars(self)
        self._status = EditorStatusBar(self)
        self.setStatusBar(self._status)

        build_editor_menus(
            self,
            self._docks,
            self._toolbars,
            self._viewmodel.catalog,
            on_insert_symbol=self._on_insert_symbol,
            on_set_tool=self._set_tool,
            on_delete=self._delete_selection,
            on_zoom_in=lambda: self._canvas.zoom_by(1.2),
            on_zoom_out=lambda: self._canvas.zoom_by(1 / 1.2),
            on_reset_layout=self._reset_layout,
        )

        self._wire_connections()
        self._build_shortcuts()
        self._refresh_ui()
        self._set_tool(ToolMode.SELECT)

    def _delete_selection(self) -> None:
        self._viewmodel.delete_selection()

    def _wire_connections(self) -> None:
        self._toolbars.undo_action.triggered.connect(self._viewmodel.undo)
        self._toolbars.redo_action.triggered.connect(self._viewmodel.redo)
        self._toolbars.fit_action.triggered.connect(self._canvas.fit_in_view)
        self._toolbars.zoom_in_action.triggered.connect(
            lambda: self._canvas.zoom_by(1.2)
        )
        self._toolbars.zoom_out_action.triggered.connect(
            lambda: self._canvas.zoom_by(1 / 1.2)
        )

        self._palette.symbol_selected.connect(self._on_symbol_selected)
        self._navigator.symbol_selected.connect(self._on_navigator_selected)
        self._viewmodel.sheet_changed.connect(self._refresh_ui)
        self._viewmodel.status_changed.connect(self._update_status_bar)
        self._viewmodel.log_message.connect(self._messages.append_message)

        self._canvas.canvas_clicked.connect(self._viewmodel.handle_canvas_click)
        self._canvas.pin_clicked.connect(self._viewmodel.handle_pin_click)
        self._canvas.symbol_selected.connect(self._viewmodel.handle_select_symbol)
        self._canvas.wire_selected.connect(self._viewmodel.handle_select_wire)
        self._canvas.drag_started.connect(self._viewmodel.begin_drag)
        self._canvas.drag_moved.connect(self._viewmodel.drag_to)
        self._canvas.drag_finished.connect(self._viewmodel.end_drag)
        self._canvas.cursor_moved.connect(self._viewmodel.update_cursor)

        self._properties.designation_changed.connect(self._viewmodel.set_designation)
        self._properties.rotation_changed.connect(self._viewmodel.rotate_selection)
        self._properties.wire_kind_changed.connect(self._on_wire_kind_from_panel)

        self._toolbox.tool_changed.connect(self._set_tool)
        self._toolbox.wire_kind_changed.connect(self._viewmodel.set_wire_kind)

    def _build_shortcuts(self) -> None:
        delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        delete_shortcut.activated.connect(self._viewmodel.delete_selection)
        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self._viewmodel.cancel_wire)

    def _set_tool(self, mode: ToolMode) -> None:
        self._viewmodel.set_tool_mode(mode)
        self._canvas.set_tool_mode(mode)
        self._toolbox.set_tool_mode(mode)
        self._refresh_canvas()
        self._update_status_bar()

    def _on_insert_symbol(self, catalog_id: str) -> None:
        self._viewmodel.select_catalog_entry(catalog_id)
        self._palette.highlight_catalog_id(catalog_id)

    def _on_symbol_selected(self, catalog_id: str) -> None:
        self._viewmodel.select_catalog_entry(catalog_id)
        self._palette.highlight_catalog_id(catalog_id)
        self._set_tool(ToolMode.PLACE)

    def _on_navigator_selected(self, fragment_id, device_id) -> None:
        self._viewmodel.select_symbol(fragment_id, device_id)
        self._refresh_canvas()

    def _on_wire_kind_from_panel(self, kind: WireKind) -> None:
        self._viewmodel.set_wire_kind(kind)
        self._toolbox.set_wire_kind(kind)

    def _reset_layout(self) -> None:
        self._docks.reset_layout(self)

    def _refresh_ui(self) -> None:
        self._refresh_canvas()
        self._navigator.update_tree(
            self._viewmodel.project_name(),
            self._viewmodel.sheet_title(),
            self._viewmodel.build_navigator_symbols(),
        )
        props = self._viewmodel.selection_properties()
        if props:
            self._properties.update_properties(props)
        else:
            self._properties.clear()
        self._update_status_bar()

    def _refresh_canvas(self) -> None:
        overlay = self._viewmodel.build_overlay()
        self._canvas.show_sheet(
            self._viewmodel.build_sheet_view(),
            overlay,
            selected_fragment_id=self._viewmodel.selected_fragment_id,
            selected_wire_id=self._viewmodel.selected_wire_id,
            tool_mode=self._viewmodel.tool_mode,
        )

    def _update_status_bar(self) -> None:
        zoom_pct = int(self._canvas.zoom_factor() * 100)
        self._toolbars.zoom_label.setText(f" {zoom_pct}% ")
        self._status.update_from_status(self._viewmodel.build_status(), zoom_pct)
