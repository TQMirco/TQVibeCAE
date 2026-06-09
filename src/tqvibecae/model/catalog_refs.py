"""Riferimenti immutabili al catalogo libreria versionato."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

CatalogKind = Literal[
    "component",
    "symbol",
    "part",
    "footprint",
    "graphic_cell",
    "graphic_composition",
]


class CatalogReference(BaseModel):
    """Puntatore versionato a una definizione in libreria."""

    model_config = ConfigDict(frozen=True)

    definition_id: UUID
    definition_version: int
    catalog_kind: CatalogKind
