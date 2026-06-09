"""Entità base e tipi condivisi del dominio."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Entity(BaseModel):
    """Entità dominio con identità immutabile."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    entity_type: str
    human_label: str | None = None
    tags: frozenset[str] = Field(default_factory=frozenset)
    role: str | None = None


class LocalizedString(BaseModel):
    """Testo localizzabile con fallback default."""

    model_config = ConfigDict(frozen=True)

    default: str
    translations: dict[str, str] = Field(default_factory=dict)


class ProjectLocaleProfile(BaseModel):
    """Profilo locale documento progetto."""

    model_config = ConfigDict(frozen=True)

    document_languages: tuple[str, ...]
    number_format: Literal["eu", "us"] = "eu"
    ui_language_override: str | None = None


class ValidationSeverity(StrEnum):
    """Severità di un problema di validazione."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(BaseModel):
    """Problema strutturato per UI e automazioni AI."""

    model_config = ConfigDict(frozen=True)

    code: str
    severity: ValidationSeverity
    entity_path: str
    message: str
