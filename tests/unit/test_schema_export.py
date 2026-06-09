"""Verifica allineamento JSON Schema esportati con i modelli Pydantic."""

from __future__ import annotations

import json
from pathlib import Path

from tqvibecae.model.graphics.cells import GraphicCellDefinition
from tqvibecae.model.graphics.composition import SymbolGraphicComposition
from tqvibecae.model.library.catalog import SymbolDefinition
from tqvibecae.model.persistence import ProjectManifest
from tqvibecae.model.presentation import PlacedSymbol, SheetPresentation, WireGraphic
from tqvibecae.model.project import ProjectIndex
from tqvibecae.model.settings import ApplicationSettings
from tqvibecae.model.topology import ConnectionPoint, Net

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "docs" / "program" / "schemas"


def test_exported_schemas_match_models() -> None:
    expected = {
        "graphic_cell_definition.schema.json": (
            GraphicCellDefinition.model_json_schema()
        ),
        "symbol_graphic_composition.schema.json": (
            SymbolGraphicComposition.model_json_schema()
        ),
        "connection_point.schema.json": ConnectionPoint.model_json_schema(),
        "net.schema.json": Net.model_json_schema(),
        "symbol_definition.schema.json": SymbolDefinition.model_json_schema(),
        "placed_symbol.schema.json": PlacedSymbol.model_json_schema(),
        "wire_graphic.schema.json": WireGraphic.model_json_schema(),
        "sheet_presentation.schema.json": SheetPresentation.model_json_schema(),
        "project_manifest.schema.json": ProjectManifest.model_json_schema(),
        "application_settings.schema.json": ApplicationSettings.model_json_schema(),
        "project_index.schema.json": ProjectIndex.model_json_schema(),
    }
    for filename, schema in expected.items():
        path = SCHEMAS_DIR / filename
        assert path.exists(), f"Missing schema file: {path}"
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        assert on_disk == schema
