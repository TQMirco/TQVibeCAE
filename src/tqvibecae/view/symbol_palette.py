"""Palette simboli IEC con filtro e anteprima."""

from __future__ import annotations

from typing import ClassVar

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from tqvibecae.resources.iec_catalog.catalog import IecSymbolCatalog
from tqvibecae.view.symbol_preview import SymbolPreviewWidget


class SymbolPaletteView(QWidget):
    """Libreria simboli — albero + anteprima."""

    symbol_selected = Signal(str)

    CATEGORY_LABELS: ClassVar[dict[str, str]] = {
        "protection": "Protezione",
        "switching": "Commutazione",
        "control": "Comando",
        "loads": "Carichi",
        "terminals": "Morsetti",
        "reference": "Riferimento",
        "measurement": "Misura",
        "transformers": "Trasformatori",
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._catalog: IecSymbolCatalog | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filtra simboli…")
        self._filter.textChanged.connect(self._apply_filter)
        layout.addWidget(self._filter)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabel("Simboli IEC")
        self._tree.itemClicked.connect(self._on_item_clicked)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._tree, stretch=1)
        self._preview = SymbolPreviewWidget()
        layout.addWidget(self._preview)
        self._highlighted_id: str | None = None

    def load_catalog(self, catalog: IecSymbolCatalog) -> None:
        """Popola palette da catalogo."""
        self._catalog = catalog
        self._tree.clear()
        for category, entries in catalog.by_category().items():
            cat_label = self.CATEGORY_LABELS.get(category, category)
            cat_item = QTreeWidgetItem([cat_label])
            cat_item.setData(0, 256, category)
            for entry in entries:
                child = QTreeWidgetItem([entry.label])
                child.setData(0, 256, entry.catalog_id)
                child.setData(0, 257, entry.composition_ref)
                cat_item.addChild(child)
            self._tree.addTopLevelItem(cat_item)
            cat_item.setExpanded(True)

    def highlight_catalog_id(self, catalog_id: str) -> None:
        """Evidenzia voce selezionata."""
        self._highlighted_id = catalog_id
        for i in range(self._tree.topLevelItemCount()):
            cat = self._tree.topLevelItem(i)
            if cat is None:
                continue
            for j in range(cat.childCount()):
                child = cat.child(j)
                if child is None:
                    continue
                cid = child.data(0, 256)
                font = child.font(0)
                font.setBold(str(cid) == catalog_id)
                child.setFont(0, font)
                if str(cid) == catalog_id and self._catalog is not None:
                    comp_ref = child.data(0, 257)
                    self._preview.show_composition(self._catalog.library, comp_ref)

    def _apply_filter(self, text: str) -> None:
        needle = text.strip().lower()
        for i in range(self._tree.topLevelItemCount()):
            cat = self._tree.topLevelItem(i)
            if cat is None:
                continue
            visible_children = 0
            for j in range(cat.childCount()):
                child = cat.child(j)
                if child is None:
                    continue
                label = child.text(0).lower()
                show = needle in label or needle in cat.text(0).lower()
                child.setHidden(not show)
                if show:
                    visible_children += 1
            cat.setHidden(visible_children == 0 and bool(needle))

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        _ = column
        catalog_id = item.data(0, 256)
        if catalog_id and item.childCount() == 0:
            self.symbol_selected.emit(str(catalog_id))
            self.highlight_catalog_id(str(catalog_id))

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        self._on_item_clicked(item, column)
