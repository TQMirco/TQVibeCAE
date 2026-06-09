"""Impostazioni applicazione, workspace e numerazione."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tqvibecae.model.topology import GlobalNetDeclaration


class NumberingScheme(BaseModel):
    """Regole numerazione componenti e fili."""

    model_config = ConfigDict(frozen=True)

    component_scope: Literal["global", "per_function", "per_sheet"] = "global"
    wire_scope: Literal["sequential", "per_potential"] = "sequential"


class ApplicationSettings(BaseModel):
    """Impostazioni globali applicazione."""

    library_db_path: str = ""
    default_projects_path: str = ""
    ui_language: str = "it"
    theme: str = "system"
    autosave_interval_sec: int = Field(default=300, ge=0)
    recovery_retention_days: int = Field(default=7, ge=0)
    undo_max_depth: int = Field(default=100, ge=1)


class UserWorkspaceState(BaseModel):
    """Stato UI workspace per progetto."""

    last_sheet_id: UUID | None = None
    canvas_zoom: float = 1.0
    canvas_center_x_mm: float = 0.0
    canvas_center_y_mm: float = 0.0


class ProjectSettings(BaseModel):
    """Impostazioni progetto — precedence su ApplicationSettings."""

    model_config = ConfigDict(frozen=True)

    numbering: NumberingScheme = Field(default_factory=NumberingScheme)
    reference_standard: Literal["IEC", "NFPA"] = "IEC"
    global_nets: tuple[GlobalNetDeclaration, ...] = Field(default_factory=tuple)
    default_sheet_format: str = "A3"
