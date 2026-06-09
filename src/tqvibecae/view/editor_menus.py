"""Menu bar editor — File, Modifica, Visualizza, Inserisci, Strumenti."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMenuBar

from tqvibecae.resources.iec_catalog.catalog import IecSymbolCatalog
from tqvibecae.view.editor_docks import EditorDocks
from tqvibecae.view.editor_toolbars import EditorToolbars
from tqvibecae.viewmodel.schematic_editor_vm import ToolMode


@dataclass(frozen=True, slots=True)
class EditorMenus:
    """Menu e azioni principali."""

    bar: QMenuBar
    reset_layout_action: QAction


def build_editor_menus(
    window: QMainWindow,
    docks: EditorDocks,
    toolbars: EditorToolbars,
    catalog: IecSymbolCatalog,
    *,
    on_insert_symbol: Callable[[str], None],
    on_set_tool: Callable[[ToolMode], None],
    on_delete: Callable[[], None],
    on_zoom_in: Callable[[], None],
    on_zoom_out: Callable[[], None],
    on_reset_layout: Callable[[], None],
) -> EditorMenus:
    """Costruisce menu bar completa."""
    bar = window.menuBar()
    if bar is None:
        bar = QMenuBar(window)
        window.setMenuBar(bar)

    file_menu = bar.addMenu("&File")
    for label in ("Nuovo progetto", "Apri…", "Salva"):
        action = file_menu.addAction(label)
        action.setEnabled(False)
        action.setToolTip("Prossima versione")

    edit_menu = bar.addMenu("&Modifica")
    edit_menu.addAction(toolbars.undo_action)
    edit_menu.addAction(toolbars.redo_action)
    delete_action = edit_menu.addAction("Elimina")
    delete_action.setShortcut(QKeySequence.StandardKey.Delete)
    delete_action.triggered.connect(on_delete)

    view_menu = bar.addMenu("&Visualizza")
    view_menu.addAction(docks.panels_dock.toggleViewAction())
    view_menu.addAction(docks.properties_dock.toggleViewAction())
    view_menu.addAction(docks.messages_dock.toggleViewAction())
    view_menu.addSeparator()
    view_menu.addAction(toolbars.standard.toggleViewAction())
    view_menu.addAction(toolbars.view.toggleViewAction())
    view_menu.addSeparator()
    view_menu.addAction(toolbars.fit_action)
    zoom_in_menu = view_menu.addAction("Zoom +")
    zoom_in_menu.triggered.connect(on_zoom_in)
    zoom_out_menu = view_menu.addAction("Zoom -")
    zoom_out_menu.triggered.connect(on_zoom_out)
    view_menu.addSeparator()
    reset_layout = view_menu.addAction("Ripristina layout")
    reset_layout.triggered.connect(on_reset_layout)

    insert_menu = bar.addMenu("&Inserisci")
    category_labels = {
        "protection": "Protezione",
        "switching": "Commutazione",
        "control": "Comando",
        "loads": "Carichi",
        "terminals": "Morsetti",
        "reference": "Riferimento",
        "measurement": "Misura",
        "transformers": "Trasformatori",
    }
    for category, entries in catalog.by_category().items():
        sub = insert_menu.addMenu(category_labels.get(category, category))
        for entry in entries:
            action = sub.addAction(entry.label)

            def _make_handler(catalog_id: str) -> None:
                on_insert_symbol(catalog_id)
                on_set_tool(ToolMode.PLACE)

            action.triggered.connect(
                lambda _checked=False, cid=entry.catalog_id: _make_handler(cid)
            )

    tools_menu = bar.addMenu("&Strumenti")
    select_menu = tools_menu.addAction("Seleziona")
    select_menu.setShortcut("V")
    select_menu.triggered.connect(lambda: on_set_tool(ToolMode.SELECT))
    place_menu = tools_menu.addAction("Posiziona simbolo")
    place_menu.setShortcut("P")
    place_menu.triggered.connect(lambda: on_set_tool(ToolMode.PLACE))
    wire_menu = tools_menu.addAction("Filo")
    wire_menu.setShortcut("W")
    wire_menu.triggered.connect(lambda: on_set_tool(ToolMode.WIRE))

    help_menu = bar.addMenu("&?")
    about = help_menu.addAction("Informazioni su TQVibeCAE")
    about.setEnabled(False)

    return EditorMenus(bar=bar, reset_layout_action=reset_layout)
