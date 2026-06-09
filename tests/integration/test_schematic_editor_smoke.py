"""Smoke test editor schematico — shell Altium."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QDockWidget

from tqvibecae.view.editor_main_window import SchematicEditorWindow
from tqvibecae.view.schematic_canvas import SchematicCanvasView
from tqvibecae.view.symbol_palette import SymbolPaletteView
from tqvibecae.viewmodel.schematic_editor_vm import SchematicEditorViewModel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.mark.qt
def test_schematic_editor_ui(qapp) -> None:
    vm = SchematicEditorViewModel()
    palette = SymbolPaletteView()
    palette.load_catalog(vm.catalog)
    canvas = SchematicCanvasView()
    canvas.show_sheet(vm.build_sheet_view())
    assert palette._tree.topLevelItemCount() > 0
    assert canvas.scene().items().__len__() > 0


@pytest.mark.qt
def test_altium_shell_layout(qapp) -> None:
    window = SchematicEditorWindow()
    central = window.centralWidget()
    assert central is not None
    docks = window.findChildren(QDockWidget)
    assert len(docks) >= 3
    menu = window.menuBar()
    assert menu is not None
    titles = [action.text() for action in menu.actions()]
    assert any("Visualizza" in t for t in titles)


@pytest.mark.qt
def test_navigator_lists_symbols_after_place(qapp) -> None:
    vm = SchematicEditorViewModel()
    assert vm.build_navigator_symbols() == ()
    entry = vm.catalog.entries[0]
    vm.select_catalog_entry(entry.catalog_id)
    vm.update_cursor(50.0, 50.0)
    vm.handle_canvas_click(50.0, 50.0)
    symbols = vm.build_navigator_symbols()
    assert len(symbols) == 1
    _, _, designation = symbols[0]
    assert designation


@pytest.mark.qt
def test_view_menu_toggles_panels_dock(qapp) -> None:
    window = SchematicEditorWindow()
    window.show()
    qapp.processEvents()
    dock = window._docks.panels_dock
    assert dock.isVisible()
    dock.hide()
    qapp.processEvents()
    assert not dock.isVisible()
    dock.show()
    qapp.processEvents()
    assert dock.isVisible()
