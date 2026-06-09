"""Registro dock editor — layout Altium-like."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QMainWindow,
    QTabWidget,
    QWidget,
)


class DockId(StrEnum):
    """Identificatori dock stabili."""

    PANELS = "panels"
    PROPERTIES = "properties"
    MESSAGES = "messages"


@dataclass
class EditorDocks:
    """Dock widget registrati sulla finestra principale."""

    panels_dock: QDockWidget
    panels_tabs: QTabWidget
    navigator_widget: QWidget
    library_widget: QWidget
    properties_dock: QDockWidget
    properties_widget: QWidget
    messages_dock: QDockWidget
    messages_widget: QWidget
    _default_state: QByteArray | None = None

    def capture_default_state(self, window: QMainWindow) -> None:
        self._default_state = window.saveState()

    def reset_layout(self, window: QMainWindow) -> None:
        if self._default_state is not None:
            window.restoreState(self._default_state)

    def dock_for(self, dock_id: DockId) -> QDockWidget:
        mapping = {
            DockId.PANELS: self.panels_dock,
            DockId.PROPERTIES: self.properties_dock,
            DockId.MESSAGES: self.messages_dock,
        }
        return mapping[dock_id]


def build_editor_docks(
    window: QMainWindow,
    navigator: QWidget,
    library: QWidget,
    properties: QWidget,
    messages: QWidget,
) -> EditorDocks:
    """Crea e posiziona dock sulla finestra."""
    panels_tabs = QTabWidget()
    panels_tabs.addTab(navigator, "Navigatore")
    panels_tabs.addTab(library, "Libreria")

    panels_dock = QDockWidget("Pannelli", window)
    panels_dock.setObjectName(DockId.PANELS)
    panels_dock.setWidget(panels_tabs)
    panels_dock.setMinimumWidth(220)
    window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, panels_dock)

    properties_dock = QDockWidget("Proprietà", window)
    properties_dock.setObjectName(DockId.PROPERTIES)
    properties_dock.setWidget(properties)
    properties_dock.setMinimumWidth(220)
    window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, properties_dock)

    messages_dock = QDockWidget("Messaggi", window)
    messages_dock.setObjectName(DockId.MESSAGES)
    messages_dock.setWidget(messages)
    messages_dock.setMinimumHeight(100)
    window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, messages_dock)
    messages_dock.hide()

    docks = EditorDocks(
        panels_dock=panels_dock,
        panels_tabs=panels_tabs,
        navigator_widget=navigator,
        library_widget=library,
        properties_dock=properties_dock,
        properties_widget=properties,
        messages_dock=messages_dock,
        messages_widget=messages,
    )
    docks.capture_default_state(window)
    return docks
