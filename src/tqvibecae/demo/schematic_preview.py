"""Demo anteprima schematica — entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from tqvibecae.view.schematic_canvas import SchematicCanvasView
from tqvibecae.viewmodel.schematic_preview_vm import SchematicPreviewViewModel


class SchematicPreviewWindow(QMainWindow):
    """Finestra demo con canvas schematico."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TQVibeCAE — Demo schematico")
        self.resize(900, 600)

        self._viewmodel = SchematicPreviewViewModel(self)
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self._canvas = SchematicCanvasView(central)
        layout.addWidget(self._canvas)
        self.setCentralWidget(central)

        self._canvas.show_placements(self._viewmodel.placements)


def main() -> int:
    """Avvia la demo canvas schematico."""
    app = QApplication(sys.argv)
    window = SchematicPreviewWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
