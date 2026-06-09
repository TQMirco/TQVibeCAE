"""Topologia elettrica — grafo Net, ConnectionPoint, cavi."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from tqvibecae.model.base import Entity
from tqvibecae.model.entity_types import CABLE, CONNECTION_POINT, CORE, NET


class LengthSpecification(BaseModel):
    """Lunghezza cavo con origine del dato."""

    model_config = ConfigDict(frozen=True)

    value_mm: float = Field(gt=0.0)
    source: Literal["estimated", "measured", "customer", "calculated"]
    tolerance_mm: float | None = None


class ConnectionPoint(Entity):
    """Nodo collegabile — pin, morsetto, bobina."""

    entity_type: str = CONNECTION_POINT
    device_id: UUID | None = None
    symbol_pin_id: str | None = None
    sheet_id: UUID | None = None


class Net(Entity):
    """Insieme topologico di connection point connessi."""

    entity_type: str = NET
    connection_point_ids: tuple[UUID, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _validate_connection_count(self) -> Net:
        if self.connection_point_ids and len(self.connection_point_ids) < 2:
            msg = "Net requires at least 2 connection points when non-empty"
            raise ValueError(msg)
        return self


class Core(Entity):
    """Anima di cavo — filo unipolare = cavo 1 core."""

    entity_type: str = CORE
    color_code: str
    cross_section_mm2: float = Field(gt=0.0)
    connection_point_ids: tuple[UUID, ...] = Field(default_factory=tuple)


class Cable(Entity):
    """Cavo con una o piu anime."""

    entity_type: str = CABLE
    designation: str
    cores: tuple[Core, ...]
    length: LengthSpecification | None = None
    cable_kind: str = "power"


class PotentialAssignment(BaseModel):
    """Potenziale elettrico opzionale su una net."""

    model_config = ConfigDict(frozen=True)

    net_id: UUID
    potential_label: str


class GlobalNetDeclaration(BaseModel):
    """Net globale progetto (PE, N, ...)."""

    model_config = ConfigDict(frozen=True)

    name: str
    potential_label: str
