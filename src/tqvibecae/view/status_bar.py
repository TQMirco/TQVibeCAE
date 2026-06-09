"""Status bar segmentata stile CAD."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QStatusBar, QWidget

from tqvibecae.viewmodel.schematic_editor_vm import EditorStatusView, ToolMode

_TOOL_LABELS = {
    ToolMode.SELECT: "Seleziona",
    ToolMode.PLACE: "Simbolo",
    ToolMode.WIRE: "Filo",
}


class EditorStatusBar(QStatusBar):
    """Barra stato con widget permanenti."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tool = QLabel("Seleziona")
        self._coords = QLabel("X: 0.0 mm  Y: 0.0 mm")
        self._snap = QLabel("Snap: 10 mm")
        self._zoom = QLabel("Zoom: 100%")
        for widget in (self._tool, self._coords, self._snap, self._zoom):
            widget.setMinimumWidth(80)
            self.addPermanentWidget(widget)

    def update_from_status(self, status: EditorStatusView, zoom_pct: int) -> None:
        self._tool.setText(_TOOL_LABELS.get(status.tool_mode, "—"))
        self._coords.setText(
            f"X: {status.cursor_x_mm:.1f} mm  Y: {status.cursor_y_mm:.1f} mm"
        )
        self._snap.setText(f"Snap: {status.snap_x_mm:.0f} mm")
        self._zoom.setText(f"Zoom: {zoom_pct}%")
        self.showMessage(status.message)
