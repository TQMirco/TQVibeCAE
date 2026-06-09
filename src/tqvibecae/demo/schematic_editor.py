"""Editor schematico CAD — entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from tqvibecae.view.editor_main_window import SchematicEditorWindow

_STYLE_PATH = (
    Path(__file__).resolve().parents[1] / "resources" / "styles" / "editor.qss"
)


def _load_stylesheet(app: QApplication) -> None:
    if _STYLE_PATH.is_file():
        app.setStyleSheet(_STYLE_PATH.read_text(encoding="utf-8"))


def main() -> int:
    """Avvia editor schematico CAD."""
    app = QApplication(sys.argv)
    _load_stylesheet(app)
    window = SchematicEditorWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
