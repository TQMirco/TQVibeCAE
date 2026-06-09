"""Contratti persistenza progetto .tqvibe/."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ShardRef(BaseModel):
    """Riferimento a uno shard JSON del progetto."""

    model_config = ConfigDict(frozen=True)

    path: str
    entity_type: str
    checksum_sha256: str | None = None


class ProjectManifest(BaseModel):
    """Manifest root cartella .tqvibe/."""

    model_config = ConfigDict(frozen=True)

    schema_version: int = Field(default=1, ge=1)
    project_id: UUID
    shards: tuple[ShardRef, ...] = Field(default_factory=tuple)
    saved_at: datetime


class RecoverySnapshotMeta(BaseModel):
    """Metadati snapshot recovery temporaneo."""

    model_config = ConfigDict(frozen=True)

    project_id: UUID
    recovery_path: str
    created_at: datetime
    base_manifest_checksum: str | None = None


class SavePolicy(BaseModel):
    """Policy scrittura atomica progetto."""

    model_config = ConfigDict(frozen=True)

    atomic_write: bool = True
    update_index_on_save: bool = True
