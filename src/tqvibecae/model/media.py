"""Allegati multimediali su catalogo e device."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from tqvibecae.model.base import Entity, LocalizedString
from tqvibecae.model.entity_types import MEDIA_ATTACHMENT


class MediaKind(StrEnum):
    """Tipo di allegato multimediale."""

    IMAGE = "image"
    DOCUMENT = "document"
    PHOTO = "photo"
    ICON = "icon"
    OTHER = "other"


class MediaAttachment(Entity):
    """Metadati di un file allegato (blob su filesystem)."""

    entity_type: str = MEDIA_ATTACHMENT
    kind: MediaKind
    mime_type: str
    file_ref: str
    title: LocalizedString
    description: LocalizedString | None = None
    language: str | None = None
    source_url: str | None = None
    checksum_sha256: str | None = None


class MediaAttachmentRef(BaseModel):
    """Riferimento leggero a un allegato."""

    model_config = ConfigDict(frozen=True)

    attachment_id: UUID
    role: str | None = None


class HasMediaAttachments(BaseModel):
    """Mixin opzionale per entità con allegati."""

    media: tuple[MediaAttachmentRef, ...] = Field(default_factory=tuple)
