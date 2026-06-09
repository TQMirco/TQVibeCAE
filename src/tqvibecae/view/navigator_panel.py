"""Pannello navigatore progetto/foglio/simboli."""

from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class NavigatorPanel(QWidget):
    """Albero progetto — foglio attivo e simboli piazzati."""

    symbol_selected = Signal(object, object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabel("Navigatore")
        self._tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._tree)

    def update_tree(
        self,
        project_name: str,
        sheet_title: str,
        symbols: tuple[tuple[UUID, UUID, str], ...],
    ) -> None:
        """Aggiorna albero: (fragment_id, device_id, designation)."""
        self._tree.clear()
        project_item = QTreeWidgetItem([project_name])
        sheet_item = QTreeWidgetItem([sheet_title])
        project_item.addChild(sheet_item)
        for fragment_id, device_id, designation in symbols:
            sym_item = QTreeWidgetItem([designation or "(senza nome)"])
            sym_item.setData(0, 256, (fragment_id, device_id))
            sheet_item.addChild(sym_item)
        self._tree.addTopLevelItem(project_item)
        project_item.setExpanded(True)
        sheet_item.setExpanded(True)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        _ = column
        data = item.data(0, 256)
        if data and item.childCount() == 0 and item.parent() is not None:
            fragment_id, device_id = data
            self.symbol_selected.emit(fragment_id, device_id)
