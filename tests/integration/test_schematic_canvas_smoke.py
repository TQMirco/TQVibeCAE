"""Smoke test canvas schematico PySide6."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from tqvibecae.view.schematic_canvas import SchematicCanvasView
from tqvibecae.viewmodel.schematic_preview_vm import SchematicPreviewViewModel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.mark.qt
def test_schematic_canvas_populates_scene(qapp) -> None:
    viewmodel = SchematicPreviewViewModel()
    canvas = SchematicCanvasView()
    canvas.show_placements(viewmodel.placements)
    assert canvas.scene().items().__len__() > 0
