"""Property-based tests su modelli grafici."""

from __future__ import annotations

from hypothesis import given, settings
from tests.strategies.graphics_strategies import graphic_cells

from tqvibecae.model.graphics.cells import GraphicCellDefinition


@given(cell=graphic_cells)
@settings(max_examples=100)
def test_graphic_cell_hypothesis_roundtrip(cell: GraphicCellDefinition) -> None:
    data = cell.model_dump(mode="json")
    restored = GraphicCellDefinition.model_validate(data)
    assert restored == cell
