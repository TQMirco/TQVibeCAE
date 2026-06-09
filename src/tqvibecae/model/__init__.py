"""Modello dominio TQVibeCAE — entità Pydantic v2."""

from tqvibecae.model.base import (
    Entity,
    LocalizedString,
    ProjectLocaleProfile,
    ValidationIssue,
    ValidationSeverity,
)
from tqvibecae.model.catalog_refs import CatalogKind, CatalogReference
from tqvibecae.model.device import (
    Device,
    SchematicFragment,
    StructuredDesignation,
    SubComponent,
)
from tqvibecae.model.graphics import (
    GraphicCellDefinition,
    GraphicCellInstance,
    GraphicPrimitive,
    GraphicTransform,
    PinAnchor,
    PinMapping,
    SymbolGraphicComposition,
)
from tqvibecae.model.library import (
    ComponentDefinition,
    ConnectionPointTemplate,
    FootprintDefinition,
    PartNumber,
    SymbolDefinition,
)
from tqvibecae.model.media import MediaAttachment, MediaAttachmentRef, MediaKind
from tqvibecae.model.persistence import (
    ProjectManifest,
    RecoverySnapshotMeta,
    SavePolicy,
    ShardRef,
)
from tqvibecae.model.presentation import (
    PlacedSymbol,
    SheetPresentation,
    SymbolGraphic,
    WireGraphic,
    WireKind,
    WireSegment,
    pin_ref,
)
from tqvibecae.model.project import (
    Project,
    ProjectDocument,
    ProjectIndex,
    ProjectSettings,
    Sheet,
)
from tqvibecae.model.settings import (
    ApplicationSettings,
    NumberingScheme,
    UserWorkspaceState,
)
from tqvibecae.model.topology import (
    Cable,
    ConnectionPoint,
    Core,
    GlobalNetDeclaration,
    LengthSpecification,
    Net,
    PotentialAssignment,
)

__all__ = [
    "ApplicationSettings",
    "Cable",
    "CatalogKind",
    "CatalogReference",
    "ComponentDefinition",
    "ConnectionPoint",
    "ConnectionPointTemplate",
    "Core",
    "Device",
    "Entity",
    "FootprintDefinition",
    "GlobalNetDeclaration",
    "GraphicCellDefinition",
    "GraphicCellInstance",
    "GraphicPrimitive",
    "GraphicTransform",
    "LengthSpecification",
    "LocalizedString",
    "MediaAttachment",
    "MediaAttachmentRef",
    "MediaKind",
    "Net",
    "NumberingScheme",
    "PartNumber",
    "PinAnchor",
    "PinMapping",
    "PlacedSymbol",
    "PotentialAssignment",
    "Project",
    "ProjectDocument",
    "ProjectIndex",
    "ProjectLocaleProfile",
    "ProjectManifest",
    "ProjectSettings",
    "RecoverySnapshotMeta",
    "SavePolicy",
    "SchematicFragment",
    "ShardRef",
    "Sheet",
    "SheetPresentation",
    "StructuredDesignation",
    "SubComponent",
    "SymbolDefinition",
    "SymbolGraphic",
    "SymbolGraphicComposition",
    "UserWorkspaceState",
    "ValidationIssue",
    "ValidationSeverity",
    "WireGraphic",
    "WireKind",
    "WireSegment",
    "pin_ref",
]
