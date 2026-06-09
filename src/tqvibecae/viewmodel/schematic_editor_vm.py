"""ViewModel editor schematico CAD."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from PySide6.QtCore import QObject, Signal

from tqvibecae.commands.command_bus import CommandBus
from tqvibecae.commands.connect_helpers import build_connect_pins_command
from tqvibecae.commands.delete_device import DeleteDeviceCommand
from tqvibecae.commands.delete_wire import DeleteWireCommand
from tqvibecae.commands.move_helpers import (
    build_move_device_command,
    build_rotate_device_command,
)
from tqvibecae.commands.place_device import PlaceDeviceCommand
from tqvibecae.commands.project_factory import create_empty_project
from tqvibecae.commands.set_designation import SetDesignationCommand
from tqvibecae.commands.set_wire_kind import SetWireKindCommand
from tqvibecae.model.presentation import WireKind, WireSegment
from tqvibecae.model.settings import ApplicationSettings
from tqvibecae.resources.iec_catalog.catalog import (
    IecSymbolCatalog,
    build_standard_catalog,
)
from tqvibecae.services.rendering.graphic_resolver import (
    GraphicCompositionResolver,
    ResolvedGraphic,
    resolve_placed_symbol,
)
from tqvibecae.services.rendering.wire_router import route_orthogonal


class ToolMode(StrEnum):
    """Strumento attivo editor."""

    SELECT = "select"
    PLACE = "place"
    WIRE = "wire"


@dataclass(frozen=True, slots=True)
class ResolvedPlacement:
    """Simbolo risolto per canvas."""

    label: str
    graphic: ResolvedGraphic


@dataclass(frozen=True, slots=True)
class PinHit:
    """Pin cliccabile sul canvas."""

    connection_point_id: UUID
    x_mm: float
    y_mm: float
    device_id: UUID


@dataclass(frozen=True, slots=True)
class EditorSheetView:
    """Vista foglio per rendering."""

    placements: tuple[ResolvedPlacement, ...]
    wires: tuple[object, ...]
    pin_hits: tuple[PinHit, ...]
    grid_mm: float
    fragment_ids: tuple[UUID, ...] = ()
    device_ids: tuple[UUID, ...] = ()


@dataclass(frozen=True, slots=True)
class EditorOverlayView:
    """Overlay anteprima filo / snap crosshair."""

    preview_wire_segments: tuple[WireSegment, ...] = ()
    snap_x_mm: float | None = None
    snap_y_mm: float | None = None


@dataclass(frozen=True, slots=True)
class EditorStatusView:
    """Stato per status bar."""

    tool_mode: ToolMode
    cursor_x_mm: float
    cursor_y_mm: float
    snap_x_mm: float
    snap_y_mm: float
    message: str
    selected_catalog_id: str | None


class SchematicEditorViewModel(QObject):
    """Orchestrazione editor — mutazioni via CommandBus."""

    sheet_changed = Signal()
    status_changed = Signal()
    log_message = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._catalog = build_standard_catalog()
        self._bus = CommandBus(create_empty_project(), ApplicationSettings())
        self._resolver = GraphicCompositionResolver(self._catalog.library)
        self._tool_mode = ToolMode.SELECT
        self._selected_catalog_id: str | None = None
        self._wire_start_cp: UUID | None = None
        self._designation_counters: dict[str, int] = {}
        self._selected_fragment_id: UUID | None = None
        self._selected_wire_id: UUID | None = None
        self._selected_device_id: UUID | None = None
        self._wire_kind = WireKind.CONTROL
        self._cursor_x_mm = 0.0
        self._cursor_y_mm = 0.0
        self._snap_x_mm = 0.0
        self._snap_y_mm = 0.0
        self._drag_fragment_id: UUID | None = None
        self._drag_start_x = 0.0
        self._drag_start_y = 0.0
        self._drag_origin_x = 0.0
        self._drag_origin_y = 0.0

    @property
    def command_bus(self) -> CommandBus:
        return self._bus

    @property
    def catalog(self) -> IecSymbolCatalog:
        return self._catalog

    @property
    def tool_mode(self) -> ToolMode:
        return self._tool_mode

    @property
    def wire_kind(self) -> WireKind:
        return self._wire_kind

    @property
    def selected_fragment_id(self) -> UUID | None:
        return self._selected_fragment_id

    @property
    def selected_wire_id(self) -> UUID | None:
        return self._selected_wire_id

    @property
    def selected_device_id(self) -> UUID | None:
        return self._selected_device_id

    def project_name(self) -> str:
        return self._bus.document.project.name

    def sheet_title(self) -> str:
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None:
            return "Schema"
        sheet = self._bus.document.sheets.get(sheet_id)
        return sheet.title if sheet else "Schema 1"

    def build_navigator_symbols(self) -> tuple[tuple[UUID, UUID, str], ...]:
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None:
            return ()
        presentation = self._bus.document.presentations.get(sheet_id)
        if presentation is None:
            return ()
        result: list[tuple[UUID, UUID, str]] = []
        for placed in presentation.symbols:
            designation = placed.designation or ""
            if not designation:
                device = self._bus.document.devices.get(placed.device_id)
                if device is not None:
                    designation = device.designation.component_designator
            result.append((placed.fragment_id, placed.device_id, designation))
        return tuple(result)

    def select_symbol(self, fragment_id: UUID, device_id: UUID) -> None:
        self._tool_mode = ToolMode.SELECT
        self._selected_fragment_id = fragment_id
        self._selected_device_id = device_id
        self._selected_wire_id = None
        self.sheet_changed.emit()
        self._emit_status()

    @property
    def selected_catalog_id(self) -> str | None:
        return self._selected_catalog_id

    def set_tool_mode(self, mode: ToolMode) -> None:
        self._tool_mode = mode
        self._wire_start_cp = None
        self._drag_fragment_id = None
        self._emit_status()

    def set_wire_kind(self, kind: WireKind) -> None:
        self._wire_kind = kind
        if self._selected_wire_id is not None:
            self._apply_wire_kind_to_selection(kind)

    def select_catalog_entry(self, catalog_id: str) -> None:
        self._selected_catalog_id = catalog_id
        self._tool_mode = ToolMode.PLACE
        self._emit_status()

    def undo(self) -> bool:
        if self._bus.undo():
            self._log("Annulla operazione")
            self.sheet_changed.emit()
            self._emit_status()
            return True
        return False

    def redo(self) -> bool:
        if self._bus.redo():
            self._log("Ripeti operazione")
            self.sheet_changed.emit()
            self._emit_status()
            return True
        return False

    def cancel_wire(self) -> None:
        self._wire_start_cp = None
        self._emit_status()

    def update_cursor(self, x_mm: float, y_mm: float) -> None:
        self._cursor_x_mm = x_mm
        self._cursor_y_mm = y_mm
        grid = self._grid_mm()
        self._snap_x_mm = round(x_mm / grid) * grid
        self._snap_y_mm = round(y_mm / grid) * grid
        self.status_changed.emit()

    def build_overlay(self) -> EditorOverlayView:
        segments: tuple[WireSegment, ...] = ()
        snap_x: float | None = None
        snap_y: float | None = None
        if self._tool_mode in {ToolMode.PLACE, ToolMode.WIRE}:
            snap_x = self._snap_x_mm
            snap_y = self._snap_y_mm
        if self._tool_mode == ToolMode.WIRE and self._wire_start_cp is not None:
            start = self._pin_position(self._wire_start_cp)
            if start is not None:
                segments = route_orthogonal(
                    start,
                    (self._snap_x_mm, self._snap_y_mm),
                    snap_mm=self._grid_mm(),
                )
        return EditorOverlayView(
            preview_wire_segments=segments,
            snap_x_mm=snap_x,
            snap_y_mm=snap_y,
        )

    def build_status(self) -> EditorStatusView:
        return EditorStatusView(
            tool_mode=self._tool_mode,
            cursor_x_mm=self._cursor_x_mm,
            cursor_y_mm=self._cursor_y_mm,
            snap_x_mm=self._snap_x_mm,
            snap_y_mm=self._snap_y_mm,
            message=self._status_message(),
            selected_catalog_id=self._selected_catalog_id,
        )

    def handle_select_symbol(self, fragment_id: UUID, device_id: UUID) -> None:
        if self._tool_mode != ToolMode.SELECT:
            return
        self._selected_fragment_id = fragment_id
        self._selected_device_id = device_id
        self._selected_wire_id = None
        self.sheet_changed.emit()
        self._emit_status()

    def handle_select_wire(self, wire_id: UUID) -> None:
        if self._tool_mode != ToolMode.SELECT:
            return
        self._selected_wire_id = wire_id
        self._selected_fragment_id = None
        self._selected_device_id = None
        self.sheet_changed.emit()
        self._emit_status()

    def handle_canvas_click(self, x_mm: float, y_mm: float) -> None:
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None:
            return
        if self._tool_mode == ToolMode.PLACE:
            self._place_symbol(self._snap_x_mm, self._snap_y_mm, sheet_id)
        elif self._tool_mode == ToolMode.WIRE:
            self._handle_wire_click(x_mm, y_mm, sheet_id)

    def handle_pin_click(self, cp_id: UUID) -> None:
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None or self._tool_mode != ToolMode.WIRE:
            return
        if self._wire_start_cp is None:
            self._wire_start_cp = cp_id
        else:
            self._connect_pins(self._wire_start_cp, cp_id, sheet_id)
            self._wire_start_cp = None
        self.sheet_changed.emit()
        self._emit_status()

    def begin_drag(
        self, fragment_id: UUID, device_id: UUID, x_mm: float, y_mm: float
    ) -> None:
        if self._tool_mode != ToolMode.SELECT:
            return
        placed = self._find_placed(fragment_id)
        if placed is None:
            return
        self._drag_fragment_id = fragment_id
        self._selected_device_id = device_id
        self._selected_fragment_id = fragment_id
        self._drag_start_x = x_mm
        self._drag_start_y = y_mm
        self._drag_origin_x = placed.x_mm
        self._drag_origin_y = placed.y_mm

    def drag_to(self, x_mm: float, y_mm: float) -> None:
        if self._drag_fragment_id is None:
            return
        grid = self._grid_mm()
        dx = round((x_mm - self._drag_start_x) / grid) * grid
        dy = round((y_mm - self._drag_start_y) / grid) * grid
        self._snap_x_mm = self._drag_origin_x + dx
        self._snap_y_mm = self._drag_origin_y + dy
        self.status_changed.emit()

    def end_drag(self) -> None:
        if self._drag_fragment_id is None or self._selected_device_id is None:
            return
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None:
            return
        placed = self._find_placed(self._drag_fragment_id)
        if placed is None:
            self._drag_fragment_id = None
            return
        if (
            abs(placed.x_mm - self._snap_x_mm) < 1e-9
            and abs(placed.y_mm - self._snap_y_mm) < 1e-9
        ):
            self._drag_fragment_id = None
            return
        command = build_move_device_command(
            self._bus.document,
            self._catalog.library,
            placed,
            self._snap_x_mm,
            self._snap_y_mm,
        )
        self._bus.execute(command)
        self._drag_fragment_id = None
        self.sheet_changed.emit()
        self._emit_status()

    def delete_selection(self) -> bool:
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None:
            return False
        if self._selected_wire_id is not None:
            self._bus.execute(
                DeleteWireCommand(
                    wire_id=self._selected_wire_id,
                    sheet_id=sheet_id,
                )
            )
            self._log("Eliminato filo")
            self._selected_wire_id = None
            self.sheet_changed.emit()
            self._emit_status()
            return True
        if self._selected_fragment_id is not None and self._selected_device_id:
            self._bus.execute(
                DeleteDeviceCommand(
                    device_id=self._selected_device_id,
                    fragment_id=self._selected_fragment_id,
                    sheet_id=sheet_id,
                )
            )
            self._log("Eliminato simbolo")
            self._selected_fragment_id = None
            self._selected_device_id = None
            self.sheet_changed.emit()
            self._emit_status()
            return True
        return False

    def set_designation(self, designation: str) -> None:
        if self._selected_device_id is None:
            return
        device = self._bus.document.devices.get(self._selected_device_id)
        if device is None:
            return
        old = device.designation.component_designator
        if old == designation:
            return
        self._bus.execute(
            SetDesignationCommand(
                device_id=self._selected_device_id,
                new_designation=designation,
                old_designation=old,
            )
        )
        self._update_placed_designation(designation)
        self.sheet_changed.emit()

    def rotate_selection(self, rotate_deg: float) -> None:
        if self._selected_fragment_id is None or self._selected_device_id is None:
            return
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None:
            return
        placed = self._find_placed(self._selected_fragment_id)
        if placed is None:
            return
        command = build_rotate_device_command(
            self._bus.document,
            self._catalog.library,
            placed,
            rotate_deg,
        )
        self._bus.execute(command)
        self.sheet_changed.emit()

    def selection_properties(self) -> dict[str, str]:
        props: dict[str, str] = {}
        if self._selected_device_id is not None:
            device = self._bus.document.devices.get(self._selected_device_id)
            placed = (
                self._find_placed(self._selected_fragment_id)
                if self._selected_fragment_id
                else None
            )
            if device is not None:
                props["designation"] = device.designation.component_designator
            if placed is not None:
                props["rotate_deg"] = str(placed.rotate_deg)
                cp_count = sum(
                    1
                    for cp in self._bus.document.connection_points.values()
                    if cp.device_id == self._selected_device_id
                )
                props["pin_count"] = str(cp_count)
        if self._selected_wire_id is not None:
            sheet_id = self._bus.document.active_sheet_id
            if sheet_id is not None:
                presentation = self._bus.document.presentations.get(sheet_id)
                if presentation is not None:
                    for wire in presentation.wires:
                        if wire.wire_id == self._selected_wire_id:
                            props["wire_kind"] = wire.wire_kind.value
                            props["net_id"] = str(wire.net_id or "")
                            break
        return props

    def _apply_wire_kind_to_selection(self, kind: WireKind) -> None:
        if self._selected_wire_id is None:
            return
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None:
            return
        presentation = self._bus.document.presentations.get(sheet_id)
        if presentation is None:
            return
        for wire in presentation.wires:
            if wire.wire_id == self._selected_wire_id:
                self._bus.execute(
                    SetWireKindCommand(
                        wire_id=self._selected_wire_id,
                        sheet_id=sheet_id,
                        new_kind=kind,
                        old_kind=wire.wire_kind,
                    )
                )
                self.sheet_changed.emit()
                break

    def _handle_wire_click(self, x_mm: float, y_mm: float, sheet_id: UUID) -> None:
        hit = self._find_pin_at(x_mm, y_mm)
        if hit is None:
            return
        if self._wire_start_cp is None:
            self._wire_start_cp = hit.connection_point_id
        else:
            self._connect_pins(self._wire_start_cp, hit.connection_point_id, sheet_id)
            self._wire_start_cp = None
        self.sheet_changed.emit()
        self._emit_status()

    def _place_symbol(self, x_mm: float, y_mm: float, sheet_id: UUID) -> None:
        if not self._selected_catalog_id:
            return
        entry = self._catalog.get(self._selected_catalog_id)
        if entry is None:
            return
        composition = self._catalog.library.get_composition(entry.composition_ref)
        device_id = uuid4()
        fragment_id = uuid4()
        designation = self._next_designation(entry.catalog_id)
        connection_points: list[tuple[UUID, str]] = []
        seen_pins: set[str] = set()
        for mapping in composition.pin_map:
            if mapping.symbol_pin_id in seen_pins:
                continue
            seen_pins.add(mapping.symbol_pin_id)
            connection_points.append((uuid4(), mapping.symbol_pin_id))
        command = PlaceDeviceCommand(
            device_id=device_id,
            fragment_id=fragment_id,
            sheet_id=sheet_id,
            composition_ref=entry.composition_ref,
            x_mm=x_mm,
            y_mm=y_mm,
            designation=designation,
            connection_points=tuple(connection_points),
        )
        self._bus.execute(command)
        self._log(f"Posizionato {designation} ({entry.label})")
        self.sheet_changed.emit()
        self._emit_status()

    def _connect_pins(self, from_cp: UUID, to_cp: UUID, sheet_id: UUID) -> None:
        if from_cp == to_cp:
            return
        doc = self._bus.document
        cp_from = doc.connection_points.get(from_cp)
        cp_to = doc.connection_points.get(to_cp)
        if cp_from is None or cp_to is None:
            return
        resolved_from = self._pin_position(from_cp)
        resolved_to = self._pin_position(to_cp)
        if resolved_from is None or resolved_to is None:
            return
        segments = route_orthogonal(
            resolved_from,
            resolved_to,
            snap_mm=self._grid_mm(),
        )
        kind = self._infer_wire_kind(from_cp, to_cp)
        command = build_connect_pins_command(
            doc,
            sheet_id,
            from_cp,
            to_cp,
            segments,
            kind,
        )
        self._bus.execute(command)
        self._log(f"Collegato filo ({kind.value})")
        self.sheet_changed.emit()

    def _infer_wire_kind(self, from_cp: UUID, to_cp: UUID) -> WireKind:
        doc = self._bus.document
        for cp_id in (from_cp, to_cp):
            cp = doc.connection_points.get(cp_id)
            if cp is not None and cp.symbol_pin_id and "PE" in cp.symbol_pin_id.upper():
                return WireKind.PE
        return self._wire_kind

    def _pin_position(self, cp_id: UUID) -> tuple[float, float] | None:
        for hit in self.build_sheet_view().pin_hits:
            if hit.connection_point_id == cp_id:
                return (hit.x_mm, hit.y_mm)
        return None

    def _find_pin_at(self, x_mm: float, y_mm: float) -> PinHit | None:
        tolerance = 4.0
        for hit in self.build_sheet_view().pin_hits:
            if abs(hit.x_mm - x_mm) <= tolerance and abs(hit.y_mm - y_mm) <= tolerance:
                return hit
        return None

    def _find_placed(self, fragment_id: UUID | None):
        if fragment_id is None:
            return None
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None:
            return None
        presentation = self._bus.document.presentations.get(sheet_id)
        if presentation is None:
            return None
        for placed in presentation.symbols:
            if placed.fragment_id == fragment_id:
                return placed
        return None

    def _update_placed_designation(self, designation: str) -> None:
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None or self._selected_fragment_id is None:
            return
        presentation = self._bus.document.presentations.get(sheet_id)
        if presentation is None:
            return
        symbols = tuple(
            p.model_copy(update={"designation": designation})
            if p.fragment_id == self._selected_fragment_id
            else p
            for p in presentation.symbols
        )
        self._bus.document.presentations[sheet_id] = presentation.model_copy(
            update={"symbols": symbols}
        )

    def _cp_positions_for_device(
        self,
        pin_hits: tuple[PinHit, ...],
        device_id: UUID,
    ) -> dict[UUID, tuple[float, float]]:
        return {
            hit.connection_point_id: (hit.x_mm, hit.y_mm)
            for hit in pin_hits
            if hit.device_id == device_id
        }

    def _grid_mm(self) -> float:
        sheet_id = self._bus.document.active_sheet_id
        if sheet_id is None:
            return 10.0
        presentation = self._bus.document.presentations.get(sheet_id)
        return presentation.grid_mm if presentation else 10.0

    def _next_designation(self, catalog_id: str) -> str:
        prefixes = {
            "mcb_1p": "Q",
            "mcb_3p": "Q",
            "contactor_3p": "KM",
            "motor": "M",
            "fuse": "F",
            "lamp": "H",
            "coil": "K",
            "pushbutton_no": "S",
            "pushbutton_nc": "S",
        }
        prefix = prefixes.get(catalog_id, "-")
        count = self._designation_counters.get(prefix, 0) + 1
        self._designation_counters[prefix] = count
        return f"{prefix}{count}"

    def _status_message(self) -> str:
        if self._tool_mode == ToolMode.PLACE:
            return "Posiziona simbolo — click sul foglio"
        if self._tool_mode == ToolMode.WIRE:
            if self._wire_start_cp is None:
                return "Filo — seleziona primo pin"
            return "Filo — seleziona secondo pin (Esc annulla)"
        return "Seleziona — click simbolo/filo, trascina per spostare, Del elimina"

    def _emit_status(self) -> None:
        self.status_changed.emit()

    def _log(self, message: str) -> None:
        self.log_message.emit(message)

    def build_sheet_view(self) -> EditorSheetView:
        doc = self._bus.document
        sheet_id = doc.active_sheet_id
        if sheet_id is None:
            return EditorSheetView((), (), (), 10.0)
        presentation = doc.presentations.get(sheet_id)
        if presentation is None:
            return EditorSheetView((), (), (), 10.0)

        placements: list[ResolvedPlacement] = []
        pin_hits: list[PinHit] = []
        fragment_ids: list[UUID] = []
        device_ids: list[UUID] = []
        cp_by_device_pin: dict[tuple[UUID, str], UUID] = {}
        for cp_id, cp in doc.connection_points.items():
            if cp.device_id and cp.symbol_pin_id:
                cp_by_device_pin[(cp.device_id, cp.symbol_pin_id)] = cp_id

        for placed in presentation.symbols:
            graphic = resolve_placed_symbol(self._catalog.library, placed)
            label = placed.designation or ""
            placements.append(ResolvedPlacement(label=label, graphic=graphic))
            fragment_ids.append(placed.fragment_id)
            device_ids.append(placed.device_id)
            composition = self._catalog.library.get_composition(placed.composition_ref)
            for mapping in composition.pin_map:
                cp_id = cp_by_device_pin.get((placed.device_id, mapping.symbol_pin_id))
                if cp_id is None:
                    continue
                for pin in graphic.pin_anchors:
                    if pin.symbol_pin_id != mapping.symbol_pin_id:
                        continue
                    pin_hits.append(
                        PinHit(
                            connection_point_id=cp_id,
                            x_mm=pin.x_mm,
                            y_mm=pin.y_mm,
                            device_id=placed.device_id,
                        )
                    )
                    break

        return EditorSheetView(
            placements=tuple(placements),
            wires=presentation.wires,
            pin_hits=tuple(pin_hits),
            grid_mm=presentation.grid_mm,
            fragment_ids=tuple(fragment_ids),
            device_ids=tuple(device_ids),
        )
