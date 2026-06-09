"""Canvas schematico PySide6 — navigazione CAD e input."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor, QKeyEvent, QMouseEvent, QPainter, QWheelEvent
from PySide6.QtWidgets import QGraphicsView

from tqvibecae.view.schematic_scene import SchematicSceneController
from tqvibecae.viewmodel.schematic_editor_vm import (
    EditorOverlayView,
    EditorSheetView,
    ResolvedPlacement,
    ToolMode,
)


class SchematicCanvasView(QGraphicsView):
    """QGraphicsView CAD — pan, zoom, strumenti."""

    canvas_clicked = Signal(float, float)
    pin_clicked = Signal(object)
    symbol_selected = Signal(object, object)
    wire_selected = Signal(object)
    drag_started = Signal(object, object, float, float)
    drag_moved = Signal(float, float)
    drag_finished = Signal()
    cursor_moved = Signal(float, float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        from PySide6.QtWidgets import QGraphicsScene

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._controller = SchematicSceneController(self._scene)
        self._tool_mode = ToolMode.SELECT
        self._first_show = True
        self._pan_active = False
        self._space_pan = False
        self._pan_last_x = 0.0
        self._pan_last_y = 0.0
        self._dragging = False
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor(245, 245, 248)))
        self.setMouseTracking(True)

    @property
    def controller(self) -> SchematicSceneController:
        return self._controller

    def zoom_factor(self) -> float:
        return self.transform().m11()

    def show_sheet(
        self,
        view: EditorSheetView,
        overlay: EditorOverlayView | None = None,
        *,
        selected_fragment_id=None,
        selected_wire_id=None,
        tool_mode: ToolMode = ToolMode.SELECT,
        preserve_view: bool = True,
    ) -> None:
        """Sincronizza foglio — preserva zoom/pan dopo il primo show."""
        self._tool_mode = tool_mode
        self._controller.sync(
            view,
            overlay,
            selected_fragment_id=selected_fragment_id,
            selected_wire_id=selected_wire_id,
            tool_mode=tool_mode,
        )
        if self._first_show:
            self.fit_in_view()
            self._first_show = False
            self._controller.mark_zoom_preserved()
        elif not preserve_view:
            self.fit_in_view()

    def show_placements(self, placements: tuple[ResolvedPlacement, ...]) -> None:
        """Compatibilita demo legacy."""
        from tqvibecae.viewmodel.schematic_editor_vm import EditorSheetView

        self.show_sheet(
            EditorSheetView(placements=placements, wires=(), pin_hits=(), grid_mm=10.0)
        )

    def set_tool_mode(self, mode: ToolMode) -> None:
        self._tool_mode = mode
        self._controller.set_tool_mode(mode)

    def fit_in_view(self) -> None:
        from PySide6.QtCore import QRectF

        from tqvibecae.view.schematic_scene import SHEET_HEIGHT_MM, SHEET_WIDTH_MM

        self.fitInView(
            QRectF(0, 0, SHEET_WIDTH_MM, SHEET_HEIGHT_MM),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def zoom_by(self, factor: float) -> None:
        self.scale(factor, factor)

    def wheelEvent(self, event: QWheelEvent) -> None:
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.zoom_by(factor)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_pan = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_pan = False
            self._pan_active = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton or (
            event.button() == Qt.MouseButton.LeftButton and self._space_pan
        ):
            self._pan_active = True
            self._pan_last_x = event.position().x()
            self._pan_last_y = event.position().y()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            x_mm, y_mm = scene_pos.x(), scene_pos.y()

            if self._tool_mode == ToolMode.WIRE:
                cp_id = self._controller.find_pin_at(x_mm, y_mm)
                if cp_id is not None:
                    self.pin_clicked.emit(cp_id)
                    event.accept()
                    return

            if self._tool_mode == ToolMode.SELECT:
                symbol = self._controller.find_symbol_at(x_mm, y_mm)
                if symbol is not None:
                    self.symbol_selected.emit(symbol.fragment_id, symbol.device_id)
                    self._dragging = True
                    self.drag_started.emit(
                        symbol.fragment_id, symbol.device_id, x_mm, y_mm
                    )
                    event.accept()
                    return
                wire = self._controller.find_wire_at(x_mm, y_mm)
                if wire is not None:
                    self.wire_selected.emit(wire.wire_id)
                    event.accept()
                    return

            self.canvas_clicked.emit(x_mm, y_mm)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._pan_active:
            dx = event.position().x() - self._pan_last_x
            dy = event.position().y() - self._pan_last_y
            self._pan_last_x = event.position().x()
            self._pan_last_y = event.position().y()
            self.horizontalScrollBar().setValue(
                int(self.horizontalScrollBar().value() - dx)
            )
            self.verticalScrollBar().setValue(
                int(self.verticalScrollBar().value() - dy)
            )
            event.accept()
            return

        scene_pos = self.mapToScene(event.position().toPoint())
        self.cursor_moved.emit(scene_pos.x(), scene_pos.y())

        if self._dragging and self._tool_mode == ToolMode.SELECT:
            self.drag_moved.emit(scene_pos.x(), scene_pos.y())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._pan_active and (
            event.button() == Qt.MouseButton.MiddleButton
            or (event.button() == Qt.MouseButton.LeftButton and self._space_pan)
        ):
            self._pan_active = False
            self.setCursor(
                Qt.CursorShape.OpenHandCursor
                if self._space_pan
                else Qt.CursorShape.ArrowCursor
            )
            event.accept()
            return

        if self._dragging and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.drag_finished.emit()

        super().mouseReleaseEvent(event)
