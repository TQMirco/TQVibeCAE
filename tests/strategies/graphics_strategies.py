"""Strategie Hypothesis per modelli grafici."""

from __future__ import annotations

from hypothesis import strategies as st

from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.model.entity_types import GRAPHIC_CELL
from tqvibecae.model.graphics.cells import GraphicCellDefinition
from tqvibecae.model.graphics.primitives import GraphicPrimitive, PinAnchor

catalog_refs = st.builds(
    CatalogReference,
    definition_id=st.uuids(),
    definition_version=st.integers(min_value=1, max_value=10),
    catalog_kind=st.just("graphic_cell"),
)

graphic_primitives = st.builds(
    GraphicPrimitive,
    primitive_type=st.just("line"),
    geometry=st.fixed_dictionaries(
        {
            "x1": st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            "y1": st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            "x2": st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            "y2": st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        }
    ),
    stroke_width=st.floats(min_value=0.1, max_value=5.0, allow_nan=False),
)

pin_anchors = st.builds(
    PinAnchor,
    anchor_id=st.text(min_size=1, max_size=8, alphabet="abcdef0123456789"),
    x=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    y=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)

graphic_cells = st.builds(
    GraphicCellDefinition,
    id=st.uuids(),
    entity_type=st.just(GRAPHIC_CELL),
    name=st.text(min_size=1, max_size=20),
    category=st.sampled_from(["contact_no", "contact_nc", "coil"]),
    width_mm=st.floats(min_value=1.0, max_value=100.0, allow_nan=False),
    height_mm=st.floats(min_value=1.0, max_value=100.0, allow_nan=False),
    primitives=st.lists(graphic_primitives, min_size=1, max_size=4).map(tuple),
    pin_anchors=st.lists(pin_anchors, min_size=1, max_size=4).map(tuple),
)
