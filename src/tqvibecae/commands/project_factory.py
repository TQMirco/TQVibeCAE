"""Factory progetto vuoto e helper persistenza."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from tqvibecae.model.entity_types import PROJECT, SHEET
from tqvibecae.model.persistence import ProjectManifest, ShardRef
from tqvibecae.model.presentation import SheetPresentation
from tqvibecae.model.project import Project, ProjectDocument, Sheet


def create_empty_project(name: str = "Nuovo progetto") -> ProjectDocument:
    """Crea ProjectDocument con un foglio attivo vuoto."""
    project_id = uuid4()
    sheet_id = uuid4()
    project = Project(
        id=project_id,
        entity_type=PROJECT,
        name=name,
        sheet_ids=(str(sheet_id),),
    )
    sheet = Sheet(
        id=sheet_id,
        entity_type=SHEET,
        title="Foglio 1",
    )
    return ProjectDocument(
        project=project,
        sheets={sheet_id: sheet},
        presentations={sheet_id: SheetPresentation(sheet_id=sheet_id)},
        active_sheet_id=sheet_id,
    )


def project_to_manifest(document: ProjectDocument) -> ProjectManifest:
    """Serializza manifest stub da ProjectDocument."""
    shards = (
        ShardRef(path="project.json", entity_type=PROJECT),
        ShardRef(path="index.json", entity_type="index"),
    )
    for sheet_id in document.sheets:
        shards = (
            *shards,
            ShardRef(path=f"sheets/{sheet_id}.json", entity_type=SHEET),
        )
    return ProjectManifest(
        project_id=document.project.id,
        shards=shards,
        saved_at=datetime.now(tz=UTC),
    )
