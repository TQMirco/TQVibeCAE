"""Test interazione editor — zoom preservato, overlay."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QGraphicsScene

from tqvibecae.view.schematic_canvas import SchematicCanvasView
from tqvibecae.view.schematic_scene import SchematicSceneController
from tqvibecae.viewmodel.schematic_editor_vm import (
    EditorOverlayView,
    EditorSheetView,
    SchematicEditorViewModel,
    ToolMode,
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.mark.qt
def test_scene_controller_preserves_zoom_flag(qapp) -> None:
    scene = QGraphicsScene()
    controller = SchematicSceneController(scene)
    assert controller.zoom_preserved is False
    controller.mark_zoom_preserved()
    assert controller.zoom_preserved is True


@pytest.mark.qt
def test_canvas_keeps_zoom_after_refresh(qapp) -> None:
    vm = SchematicEditorViewModel()
    canvas = SchematicCanvasView()
    canvas.show_sheet(vm.build_sheet_view(), tool_mode=ToolMode.SELECT)
    canvas.zoom_by(1.5)
    zoom_before = canvas.zoom_factor()
    canvas.show_sheet(
        vm.build_sheet_view(),
        vm.build_overlay(),
        tool_mode=vm.tool_mode,
    )
    assert canvas.controller.zoom_preserved is True
    assert canvas.zoom_factor() == pytest.approx(zoom_before, rel=0.01)


@pytest.mark.qt
def test_overlay_snap_crosshair(qapp) -> None:
    scene = QGraphicsScene()
    controller = SchematicSceneController(scene)
    view = EditorSheetView((), (), (), 10.0)
    overlay = EditorOverlayView(snap_x_mm=20.0, snap_y_mm=30.0)
    controller.sync(view, overlay, tool_mode=ToolMode.PLACE)
    assert len(scene.items()) > 0
