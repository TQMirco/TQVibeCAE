"""Anteprima mini simbolo per libreria."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.services.rendering.graphic_resolver import (
    GraphicCompositionResolver,
    InMemoryGraphicLibrary,
)


class SymbolPreviewWidget(QLabel):
    """Render composizione catalogo in anteprima 128x128."""

    PREVIEW_SIZE = 128

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(self.PREVIEW_SIZE)
        self.setMinimumWidth(self.PREVIEW_SIZE)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setText("Anteprima")
        self.setStyleSheet(
            "background: white; border: 1px solid #d0d0d8; border-radius: 4px;"
        )

    def show_composition(
        self,
        library: InMemoryGraphicLibrary,
        composition_ref: CatalogReference | None,
    ) -> None:
        if composition_ref is None:
            self.clear()
            return
        resolver = GraphicCompositionResolver(library)
        graphic = resolver.resolve(composition_ref)
        width = max(
            graphic.bbox_max_x_mm - graphic.bbox_min_x_mm,
            1.0,
        )
        height = max(
            graphic.bbox_max_y_mm - graphic.bbox_min_y_mm,
            1.0,
        )
        scale = min(
            (self.PREVIEW_SIZE - 16) / width,
            (self.PREVIEW_SIZE - 16) / height,
        )
        img = QImage(self.PREVIEW_SIZE, self.PREVIEW_SIZE, QImage.Format.Format_ARGB32)
        img.fill(0xFFFFFFFF)
        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidthF(1.0)
        painter.setPen(pen)
        offset_x = (
            (self.PREVIEW_SIZE - width * scale) / 2 - graphic.bbox_min_x_mm * scale
        )
        offset_y = (
            (self.PREVIEW_SIZE - height * scale) / 2 - graphic.bbox_min_y_mm * scale
        )
        for primitive in graphic.primitives:
            geom = primitive.geometry
            if primitive.primitive_type == "line":
                painter.drawLine(
                    int(geom["x1"] * scale + offset_x),
                    int(geom["y1"] * scale + offset_y),
                    int(geom["x2"] * scale + offset_x),
                    int(geom["y2"] * scale + offset_y),
                )
            elif primitive.primitive_type == "rect":
                painter.drawRect(
                    int(geom["x"] * scale + offset_x),
                    int(geom["y"] * scale + offset_y),
                    int(geom["width"] * scale),
                    int(geom["height"] * scale),
                )
            elif primitive.primitive_type == "circle":
                cx = geom["cx"] * scale + offset_x
                cy = geom["cy"] * scale + offset_y
                r = geom["radius"] * scale
                painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
        painter.end()
        self.setPixmap(QPixmap.fromImage(img))
        self.setText("")

    def clear(self) -> None:
        self.setPixmap(QPixmap())
        self.setText("Anteprima")
