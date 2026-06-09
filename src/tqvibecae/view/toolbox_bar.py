"""Toolbox verticale strumenti — Active Bar light."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from tqvibecae.model.presentation import WireKind
from tqvibecae.viewmodel.schematic_editor_vm import ToolMode


@dataclass(frozen=True, slots=True)
class ToolboxActions:
    """Azioni toolbox per collegamento menu/toolbar."""

    select: QAction
    place: QAction
    wire: QAction
    wire_control: QAction
    wire_power: QAction
    wire_pe: QAction


class ToolboxBar(QWidget):
    """Barra strumenti verticale affiancata al canvas."""

    tool_changed = Signal(object)
    wire_kind_changed = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(52)
        toolbar = QToolBar(self)
        toolbar.setOrientation(Qt.Orientation.Vertical)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)

        self._tool_group = QActionGroup(self)
        self._tool_group.setExclusive(True)

        self._select = QAction("Seleziona", self)
        self._select.setCheckable(True)
        self._select.setToolTip("Seleziona (V)")
        self._select.setShortcut("V")
        self._tool_group.addAction(self._select)

        self._place = QAction("Simbolo", self)
        self._place.setCheckable(True)
        self._place.setToolTip("Posiziona simbolo (P)")
        self._place.setShortcut("P")
        self._tool_group.addAction(self._place)

        self._wire = QAction("Filo", self)
        self._wire.setCheckable(True)
        self._wire.setToolTip("Collega filo (W)")
        self._wire.setShortcut("W")
        self._tool_group.addAction(self._wire)

        for action in (self._select, self._place, self._wire):
            toolbar.addAction(action)
            action.triggered.connect(self._emit_tool)

        toolbar.addSeparator()

        self._wire_kind_group = QActionGroup(self)
        self._wire_kind_group.setExclusive(True)
        self._kind_control = QAction("C", self)
        self._kind_control.setCheckable(True)
        self._kind_control.setToolTip("Filo comando")
        self._kind_power = QAction("P", self)
        self._kind_power.setCheckable(True)
        self._kind_power.setToolTip("Filo potenza")
        self._kind_pe = QAction("PE", self)
        self._kind_pe.setCheckable(True)
        self._kind_pe.setToolTip("Filo terra PE")
        self._kind_control.setChecked(True)
        for action in (self._kind_control, self._kind_power, self._kind_pe):
            self._wire_kind_group.addAction(action)
            toolbar.addAction(action)
            action.triggered.connect(self._emit_wire_kind)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(toolbar)

        self._select.setChecked(True)

    @property
    def actions_bundle(self) -> ToolboxActions:
        return ToolboxActions(
            select=self._select,
            place=self._place,
            wire=self._wire,
            wire_control=self._kind_control,
            wire_power=self._kind_power,
            wire_pe=self._kind_pe,
        )

    def set_tool_mode(self, mode: ToolMode) -> None:
        if mode == ToolMode.SELECT:
            self._select.setChecked(True)
        elif mode == ToolMode.PLACE:
            self._place.setChecked(True)
        elif mode == ToolMode.WIRE:
            self._wire.setChecked(True)

    def set_wire_kind(self, kind: WireKind) -> None:
        if kind == WireKind.CONTROL:
            self._kind_control.setChecked(True)
        elif kind == WireKind.POWER:
            self._kind_power.setChecked(True)
        elif kind == WireKind.PE:
            self._kind_pe.setChecked(True)

    def _emit_tool(self) -> None:
        if self._select.isChecked():
            self.tool_changed.emit(ToolMode.SELECT)
        elif self._place.isChecked():
            self.tool_changed.emit(ToolMode.PLACE)
        elif self._wire.isChecked():
            self.tool_changed.emit(ToolMode.WIRE)

    def _emit_wire_kind(self) -> None:
        if self._kind_control.isChecked():
            self.wire_kind_changed.emit(WireKind.CONTROL)
        elif self._kind_power.isChecked():
            self.wire_kind_changed.emit(WireKind.POWER)
        elif self._kind_pe.isChecked():
            self.wire_kind_changed.emit(WireKind.PE)
