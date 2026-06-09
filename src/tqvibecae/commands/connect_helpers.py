"""Helper costruzione ConnectPinsCommand."""

from __future__ import annotations

from uuid import UUID, uuid4

from tqvibecae.commands.connect_pins import ConnectPinsCommand
from tqvibecae.model.presentation import WireKind, WireSegment
from tqvibecae.model.project import ProjectDocument


def build_connect_pins_command(
    document: ProjectDocument,
    sheet_id: UUID,
    from_cp_id: UUID,
    to_cp_id: UUID,
    segments: tuple[WireSegment, ...],
    wire_kind: WireKind = WireKind.CONTROL,
) -> ConnectPinsCommand:
    """Prepara comando collegamento con merge net esistenti."""
    wire_id = uuid4()
    net_id = uuid4()
    merged: set[UUID] = set()
    removed = []
    prev_from: UUID | None = None
    prev_to: UUID | None = None
    for net in document.nets.values():
        if from_cp_id in net.connection_point_ids:
            merged.add(net.id)
            removed.append(net)
            prev_from = net.id
        if to_cp_id in net.connection_point_ids:
            merged.add(net.id)
            if net not in removed:
                removed.append(net)
            prev_to = net.id
    if not merged:
        merged.add(net_id)
    return ConnectPinsCommand(
        wire_id=wire_id,
        net_id=net_id,
        sheet_id=sheet_id,
        from_cp_id=from_cp_id,
        to_cp_id=to_cp_id,
        wire_kind=wire_kind,
        segments=segments,
        merged_net_ids=tuple(merged),
        removed_nets=tuple(removed),
        previous_net_id_from=prev_from,
        previous_net_id_to=prev_to,
    )
