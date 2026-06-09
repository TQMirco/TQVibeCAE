"""Resolver composizioni grafiche — coordinate normalizzate → mm assoluti."""

from __future__ import annotations

import math
from dataclasses import dataclass
from uuid import UUID

from beartype import beartype

from tqvibecae.model.catalog_refs import CatalogReference
from tqvibecae.model.graphics.cells import GraphicCellDefinition
from tqvibecae.model.graphics.composition import SymbolGraphicComposition
from tqvibecae.model.graphics.primitives import GraphicPrimitive, GraphicTransform

Point2D = tuple[float, float]


def _as_float(value: float | tuple[float, ...]) -> float:
    if isinstance(value, tuple):
        msg = "Expected scalar geometry coordinate"
        raise TypeError(msg)
    return value


@dataclass(frozen=True, slots=True)
class ResolvedPrimitive:
    """Primitiva risolta in mm assoluti sul foglio."""

    primitive_type: str
    geometry: dict[str, float]
    stroke_width: float
    layer: str


@dataclass(frozen=True, slots=True)
class ResolvedPinAnchor:
    """Pin risolto in mm assoluti."""

    symbol_pin_id: str | None
    anchor_id: str
    x_mm: float
    y_mm: float
    direction_deg: float | None


@dataclass(frozen=True, slots=True)
class ResolvedGraphic:
    """Risultato risoluzione composizione + transform foglio."""

    primitives: tuple[ResolvedPrimitive, ...]
    pin_anchors: tuple[ResolvedPinAnchor, ...]
    bbox_min_x_mm: float
    bbox_min_y_mm: float
    bbox_max_x_mm: float
    bbox_max_y_mm: float


class InMemoryGraphicLibrary:
    """Libreria grafica in memoria per demo e test."""

    def __init__(self) -> None:
        self._cells: dict[UUID, GraphicCellDefinition] = {}
        self._compositions: dict[UUID, SymbolGraphicComposition] = {}
        self._cell_versions: dict[UUID, int] = {}
        self._composition_versions: dict[UUID, int] = {}

    def register_cell(self, cell: GraphicCellDefinition, version: int = 1) -> None:
        self._cells[cell.id] = cell
        self._cell_versions[cell.id] = version

    def register_composition(
        self, composition: SymbolGraphicComposition, version: int = 1
    ) -> None:
        self._compositions[composition.id] = composition
        self._composition_versions[composition.id] = version

    def get_cell(self, ref: CatalogReference) -> GraphicCellDefinition:
        cell = self._cells.get(ref.definition_id)
        if cell is None:
            msg = f"Graphic cell not found: {ref.definition_id}"
            raise KeyError(msg)
        if self._cell_versions.get(ref.definition_id) != ref.definition_version:
            msg = f"Graphic cell version mismatch: {ref.definition_id}"
            raise KeyError(msg)
        return cell

    def get_composition(self, ref: CatalogReference) -> SymbolGraphicComposition:
        comp = self._compositions.get(ref.definition_id)
        if comp is None:
            msg = f"Graphic composition not found: {ref.definition_id}"
            raise KeyError(msg)
        if self._composition_versions.get(ref.definition_id) != ref.definition_version:
            msg = f"Graphic composition version mismatch: {ref.definition_id}"
            raise KeyError(msg)
        return comp


def _rotate_point(x: float, y: float, deg: float) -> Point2D:
    rad = math.radians(deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    return (x * cos_a - y * sin_a, x * sin_a + y * cos_a)


def _apply_transform(x: float, y: float, transform: GraphicTransform) -> Point2D:
    sx = x * transform.scale
    sy = y * transform.scale
    rx, ry = _rotate_point(sx, sy, transform.rotate_deg)
    return (rx + transform.translate_x_mm, ry + transform.translate_y_mm)


def _norm_to_cell_mm(
    x_norm: float, y_norm: float, cell: GraphicCellDefinition
) -> Point2D:
    return (x_norm * cell.width_mm, y_norm * cell.height_mm)


def _transform_primitive(
    primitive: GraphicPrimitive,
    cell: GraphicCellDefinition,
    instance_transform: GraphicTransform,
    repeat_index: int,
    repeat_spacing_mm: float,
) -> ResolvedPrimitive:
    repeat_offset_x = repeat_index * repeat_spacing_mm
    geometry: dict[str, float] = {}

    if primitive.primitive_type == "line":
        x1, y1 = _norm_to_cell_mm(
            _as_float(primitive.geometry["x1"]),
            _as_float(primitive.geometry["y1"]),
            cell,
        )
        x2, y2 = _norm_to_cell_mm(
            _as_float(primitive.geometry["x2"]),
            _as_float(primitive.geometry["y2"]),
            cell,
        )
        p1 = _apply_transform(x1 + repeat_offset_x, y1, instance_transform)
        p2 = _apply_transform(x2 + repeat_offset_x, y2, instance_transform)
        geometry = {"x1": p1[0], "y1": p1[1], "x2": p2[0], "y2": p2[1]}
    elif primitive.primitive_type == "rect":
        x = _as_float(primitive.geometry["x"]) * cell.width_mm + repeat_offset_x
        y = _as_float(primitive.geometry["y"]) * cell.height_mm
        w = _as_float(primitive.geometry["width"]) * cell.width_mm
        h = _as_float(primitive.geometry["height"]) * cell.height_mm
        p = _apply_transform(x, y, instance_transform)
        geometry = {
            "x": p[0],
            "y": p[1],
            "width": w * instance_transform.scale,
            "height": h * instance_transform.scale,
        }
    elif primitive.primitive_type == "arc":
        cx, cy = _norm_to_cell_mm(
            _as_float(primitive.geometry["cx"]),
            _as_float(primitive.geometry["cy"]),
            cell,
        )
        radius = _as_float(primitive.geometry["radius"]) * cell.width_mm
        center = _apply_transform(cx + repeat_offset_x, cy, instance_transform)
        start_deg = _as_float(primitive.geometry.get("start_deg", 0.0))
        span_deg = _as_float(primitive.geometry.get("span_deg", 180.0))
        geometry = {
            "cx": center[0],
            "cy": center[1],
            "radius": radius * instance_transform.scale,
            "start_deg": start_deg,
            "span_deg": span_deg,
        }
    elif primitive.primitive_type == "circle":
        cx, cy = _norm_to_cell_mm(
            _as_float(primitive.geometry["cx"]),
            _as_float(primitive.geometry["cy"]),
            cell,
        )
        radius = _as_float(primitive.geometry["radius"]) * cell.width_mm
        center = _apply_transform(cx + repeat_offset_x, cy, instance_transform)
        geometry = {
            "cx": center[0],
            "cy": center[1],
            "radius": radius * instance_transform.scale,
        }
    elif primitive.primitive_type == "text":
        x = _as_float(primitive.geometry["x"]) * cell.width_mm + repeat_offset_x
        y = _as_float(primitive.geometry["y"]) * cell.height_mm
        p = _apply_transform(x, y, instance_transform)
        scale = _as_float(primitive.geometry.get("text_scale", 0.1))
        text_char = _as_float(primitive.geometry.get("text_char", ord("M")))
        geometry = {
            "x": p[0],
            "y": p[1],
            "text_scale": scale * instance_transform.scale,
            "text_char": text_char,
        }
    else:
        geometry = {}

    return ResolvedPrimitive(
        primitive_type=primitive.primitive_type,
        geometry=geometry,
        stroke_width=primitive.stroke_width,
        layer=primitive.layer,
    )


def _resolve_pin(
    anchor_x_norm: float,
    anchor_y_norm: float,
    cell: GraphicCellDefinition,
    instance_transform: GraphicTransform,
    repeat_index: int,
    repeat_spacing_mm: float,
    symbol_pin_id: str | None,
    anchor_id: str,
    direction_deg: float | None,
) -> ResolvedPinAnchor:
    x_mm, y_mm = _norm_to_cell_mm(anchor_x_norm, anchor_y_norm, cell)
    wx, wy = _apply_transform(
        x_mm + repeat_index * repeat_spacing_mm, y_mm, instance_transform
    )
    resolved_direction = None
    if direction_deg is not None:
        resolved_direction = direction_deg + instance_transform.rotate_deg
    return ResolvedPinAnchor(
        symbol_pin_id=symbol_pin_id,
        anchor_id=anchor_id,
        x_mm=wx,
        y_mm=wy,
        direction_deg=resolved_direction,
    )


class GraphicCompositionResolver:
    """Risolve composizioni grafiche in primitive assolute (mm)."""

    def __init__(self, library: InMemoryGraphicLibrary) -> None:
        self._library = library

    @beartype
    def resolve(
        self,
        composition_ref: CatalogReference,
        origin_x_mm: float = 0.0,
        origin_y_mm: float = 0.0,
        rotate_deg: float = 0.0,
    ) -> ResolvedGraphic:
        """Risolve composizione con transform foglio (origine + rotazione)."""
        composition = self._library.get_composition(composition_ref)
        sheet_transform = GraphicTransform(
            translate_x_mm=origin_x_mm,
            translate_y_mm=origin_y_mm,
            rotate_deg=rotate_deg,
        )

        pin_lookup: dict[tuple[str, str], str] = {
            (mapping.cell_instance_id, mapping.cell_anchor_id): mapping.symbol_pin_id
            for mapping in composition.pin_map
        }

        primitives: list[ResolvedPrimitive] = []
        pins: list[ResolvedPinAnchor] = []

        for instance in composition.cells:
            cell = self._library.get_cell(instance.cell_ref)
            spacing = instance.repeat_spacing_mm or 0.0
            for repeat_index in range(instance.repeat_count):
                for primitive in cell.primitives:
                    resolved = _transform_primitive(
                        primitive,
                        cell,
                        instance.transform,
                        repeat_index,
                        spacing,
                    )
                    if rotate_deg != 0.0 or origin_x_mm != 0.0 or origin_y_mm != 0.0:
                        resolved = _apply_sheet_transform(resolved, sheet_transform)
                    primitives.append(resolved)

                for anchor in cell.pin_anchors:
                    instance_key = (
                        f"{instance.instance_id}#{repeat_index}"
                        if instance.repeat_count > 1
                        else instance.instance_id
                    )
                    symbol_pin = pin_lookup.get(
                        (instance.instance_id, anchor.anchor_id)
                    )
                    pin = _resolve_pin(
                        anchor.x,
                        anchor.y,
                        cell,
                        instance.transform,
                        repeat_index,
                        spacing,
                        symbol_pin,
                        f"{instance_key}:{anchor.anchor_id}",
                        anchor.direction_deg,
                    )
                    if rotate_deg != 0.0 or origin_x_mm != 0.0 or origin_y_mm != 0.0:
                        pin = _apply_sheet_transform_pin(pin, sheet_transform)
                    pins.append(pin)

        bbox = _compute_bbox(primitives, pins)
        return ResolvedGraphic(
            primitives=tuple(primitives),
            pin_anchors=tuple(pins),
            **bbox,
        )


def _apply_sheet_transform_pin(
    pin: ResolvedPinAnchor, sheet_transform: GraphicTransform
) -> ResolvedPinAnchor:
    wx, wy = _apply_transform(pin.x_mm, pin.y_mm, sheet_transform)
    direction = pin.direction_deg
    if direction is not None:
        direction += sheet_transform.rotate_deg
    return ResolvedPinAnchor(
        symbol_pin_id=pin.symbol_pin_id,
        anchor_id=pin.anchor_id,
        x_mm=wx,
        y_mm=wy,
        direction_deg=direction,
    )


def _apply_sheet_transform(
    primitive: ResolvedPrimitive, sheet_transform: GraphicTransform
) -> ResolvedPrimitive:
    geom = primitive.geometry
    if primitive.primitive_type == "line":
        x1, y1 = _apply_transform(float(geom["x1"]), float(geom["y1"]), sheet_transform)
        x2, y2 = _apply_transform(float(geom["x2"]), float(geom["y2"]), sheet_transform)
        new_geom: dict[str, float] = {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
        }
    elif primitive.primitive_type in {"rect", "circle", "arc", "text"}:
        new_geom = dict(geom)
        if "x" in geom:
            px, py = _apply_transform(
                float(geom["x"]), float(geom["y"]), sheet_transform
            )
            new_geom["x"] = px
            new_geom["y"] = py
        if "cx" in geom:
            cx, cy = _apply_transform(
                float(geom["cx"]), float(geom["cy"]), sheet_transform
            )
            new_geom["cx"] = cx
            new_geom["cy"] = cy
    else:
        new_geom = dict(geom)

    return ResolvedPrimitive(
        primitive_type=primitive.primitive_type,
        geometry=new_geom,
        stroke_width=primitive.stroke_width,
        layer=primitive.layer,
    )


def _compute_bbox(
    primitives: list[ResolvedPrimitive],
    pins: list[ResolvedPinAnchor],
) -> dict[str, float]:
    xs: list[float] = []
    ys: list[float] = []

    for primitive in primitives:
        geom = primitive.geometry
        if primitive.primitive_type == "line":
            xs.extend([float(geom["x1"]), float(geom["x2"])])
            ys.extend([float(geom["y1"]), float(geom["y2"])])
        elif primitive.primitive_type == "rect":
            x = float(geom["x"])
            y = float(geom["y"])
            xs.extend([x, x + float(geom["width"])])
            ys.extend([y, y + float(geom["height"])])
        elif primitive.primitive_type in {"circle", "arc"}:
            cx = float(geom["cx"])
            cy = float(geom["cy"])
            r = float(geom["radius"])
            xs.extend([cx - r, cx + r])
            ys.extend([cy - r, cy + r])
        elif primitive.primitive_type == "text":
            xs.append(float(geom["x"]))
            ys.append(float(geom["y"]))

    for pin in pins:
        xs.append(pin.x_mm)
        ys.append(pin.y_mm)

    if not xs:
        return {
            "bbox_min_x_mm": 0.0,
            "bbox_min_y_mm": 0.0,
            "bbox_max_x_mm": 0.0,
            "bbox_max_y_mm": 0.0,
        }

    return {
        "bbox_min_x_mm": min(xs),
        "bbox_min_y_mm": min(ys),
        "bbox_max_x_mm": max(xs),
        "bbox_max_y_mm": max(ys),
    }


def resolve_placed_symbol(
    library: InMemoryGraphicLibrary,
    placed: object,
) -> ResolvedGraphic:
    """Helper — risolve PlacedSymbol in grafica assoluta."""
    from tqvibecae.model.presentation import PlacedSymbol

    if not isinstance(placed, PlacedSymbol):
        msg = "Expected PlacedSymbol"
        raise TypeError(msg)
    resolver = GraphicCompositionResolver(library)
    return resolver.resolve(
        placed.composition_ref,
        origin_x_mm=placed.x_mm,
        origin_y_mm=placed.y_mm,
        rotate_deg=placed.rotate_deg,
    )
