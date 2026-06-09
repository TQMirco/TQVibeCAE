"""Pannello proprietà con tab e empty state."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from tqvibecae.model.presentation import WireKind


class PropertiesPanel(QWidget):
    """Dock proprietà — Generale / Collegamento."""

    designation_changed = Signal(str)
    rotation_changed = Signal(float)
    wire_kind_changed = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        self._stack = QStackedWidget()
        self._empty = QLabel("Nessuna selezione")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stack.addWidget(self._empty)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        tabs = QTabWidget()

        general = QWidget()
        general_form = QFormLayout(general)
        self._designation = QLineEdit()
        self._designation.editingFinished.connect(self._emit_designation)
        general_form.addRow("Designazione:", self._designation)
        self._rotation = QComboBox()
        for deg in (0, 90, 180, 270):
            self._rotation.addItem(f"{deg}°", deg)
        self._rotation.currentIndexChanged.connect(self._emit_rotation)
        general_form.addRow("Rotazione:", self._rotation)
        tabs.addTab(general, "Generale")

        connection = QWidget()
        conn_form = QFormLayout(connection)
        self._wire_kind = QComboBox()
        self._wire_kind.addItem("Comando", WireKind.CONTROL)
        self._wire_kind.addItem("Potenza", WireKind.POWER)
        self._wire_kind.addItem("PE", WireKind.PE)
        self._wire_kind.currentIndexChanged.connect(self._emit_wire_kind)
        conn_form.addRow("Tipo filo:", self._wire_kind)
        self._pin_count = QLabel("—")
        conn_form.addRow("Pin:", self._pin_count)
        self._net_id = QLabel("—")
        conn_form.addRow("Net:", self._net_id)
        tabs.addTab(connection, "Collegamento")

        content_layout.addWidget(tabs)
        self._stack.addWidget(content)
        root.addWidget(self._stack)
        self._block = False
        self._stack.setCurrentIndex(0)

    def update_properties(self, props: dict[str, str]) -> None:
        """Aggiorna campi da selection_properties()."""
        if not props:
            self.clear()
            return
        self._stack.setCurrentIndex(1)
        self._block = True
        if "designation" in props:
            self._designation.setText(props["designation"])
        if "rotate_deg" in props:
            deg = int(float(props["rotate_deg"]))
            idx = self._rotation.findData(deg)
            if idx >= 0:
                self._rotation.setCurrentIndex(idx)
        if "pin_count" in props:
            self._pin_count.setText(props["pin_count"])
        else:
            self._pin_count.setText("—")
        if "net_id" in props:
            self._net_id.setText(props["net_id"] or "—")
        else:
            self._net_id.setText("—")
        if "wire_kind" in props:
            kind = WireKind(props["wire_kind"])
            idx = self._wire_kind.findData(kind)
            if idx >= 0:
                self._wire_kind.setCurrentIndex(idx)
        self._block = False

    def clear(self) -> None:
        self._block = True
        self._stack.setCurrentIndex(0)
        self._designation.clear()
        self._pin_count.setText("—")
        self._net_id.setText("—")
        self._block = False

    def _emit_designation(self) -> None:
        if not self._block:
            self.designation_changed.emit(self._designation.text().strip())

    def _emit_rotation(self, index: int) -> None:
        _ = index
        if not self._block:
            deg = self._rotation.currentData()
            if deg is not None:
                self.rotation_changed.emit(float(deg))

    def _emit_wire_kind(self, index: int) -> None:
        _ = index
        if not self._block:
            kind = self._wire_kind.currentData()
            if kind is not None:
                self.wire_kind_changed.emit(kind)
