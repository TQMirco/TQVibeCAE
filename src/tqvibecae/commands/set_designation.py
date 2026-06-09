"""Comando — aggiorna designazione device."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from tqvibecae.commands.base import Command
from tqvibecae.model.device import StructuredDesignation
from tqvibecae.model.project import ProjectDocument, ProjectIndex


class SetDesignationCommand(Command):
    """Aggiorna StructuredDesignation e ProjectIndex."""

    command_type: Literal["set_designation"] = "set_designation"
    device_id: UUID
    new_designation: str
    old_designation: str

    def apply(self, document: ProjectDocument) -> None:
        device = document.devices.get(self.device_id)
        if device is None:
            return
        document.devices[self.device_id] = device.model_copy(
            update={
                "designation": StructuredDesignation(
                    function_prefix=device.designation.function_prefix,
                    location_prefix=device.designation.location_prefix,
                    component_designator=self.new_designation,
                )
            }
        )
        self._update_index(document, self.new_designation)

    def revert(self, document: ProjectDocument) -> None:
        device = document.devices.get(self.device_id)
        if device is None:
            return
        document.devices[self.device_id] = device.model_copy(
            update={
                "designation": StructuredDesignation(
                    function_prefix=device.designation.function_prefix,
                    location_prefix=device.designation.location_prefix,
                    component_designator=self.old_designation,
                )
            }
        )
        self._update_index(document, self.old_designation)

    def _update_index(self, document: ProjectDocument, designation: str) -> None:
        designations = dict(document.index.designation_to_device)
        designations.pop(self.old_designation, None)
        designations[designation] = str(self.device_id)
        document.index = ProjectIndex(
            device_to_sheets=dict(document.index.device_to_sheets),
            designation_to_device=designations,
            net_to_devices=dict(document.index.net_to_devices),
        )
