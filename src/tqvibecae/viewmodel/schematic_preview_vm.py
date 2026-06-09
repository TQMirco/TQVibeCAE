"""ViewModel per anteprima schematica demo (legacy smoke)."""

from __future__ import annotations

from PySide6.QtCore import QObject

from tqvibecae.resources.iec_graphics import build_demo_library
from tqvibecae.services.rendering.graphic_resolver import GraphicCompositionResolver
from tqvibecae.viewmodel.schematic_editor_vm import ResolvedPlacement


class SchematicPreviewViewModel(QObject):
    """Fornisce grafica risolta per la demo canvas — nessuna mutazione dominio."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        library, refs = build_demo_library()
        resolver = GraphicCompositionResolver(library)
        self._placements = (
            ResolvedPlacement(
                label="Contatto NA",
                graphic=resolver.resolve(
                    refs.single_contact, origin_x_mm=20.0, origin_y_mm=40.0
                ),
            ),
            ResolvedPlacement(
                label="3 poli",
                graphic=resolver.resolve(
                    refs.three_pole, origin_x_mm=80.0, origin_y_mm=40.0
                ),
            ),
            ResolvedPlacement(
                label="Bobina",
                graphic=resolver.resolve(
                    refs.coil, origin_x_mm=160.0, origin_y_mm=40.0
                ),
            ),
        )

    @property
    def placements(self) -> tuple[ResolvedPlacement, ...]:
        return self._placements
