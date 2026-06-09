"""Pannello messaggi operazioni editor."""

from __future__ import annotations

from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget


class MessagesPanel(QWidget):
    """Log read-only stile pannello Output Altium."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setPlaceholderText("Messaggi operazioni…")
        layout.addWidget(self._log)

    def append_message(self, text: str) -> None:
        self._log.appendPlainText(text)
