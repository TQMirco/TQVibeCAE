"""Command pattern — base e record sessione."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from tqvibecae.model.project import ProjectDocument


class Command(BaseModel, ABC):
    """Mutazione serializzabile applicabile al ProjectDocument."""

    command_type: str

    @abstractmethod
    def apply(self, document: ProjectDocument) -> None:
        """Applica la mutazione."""

    @abstractmethod
    def revert(self, document: ProjectDocument) -> None:
        """Annulla la mutazione."""


class CommandRecord(BaseModel):
    """Record eseguito nello stack undo."""

    command_type: str
    payload: dict[str, object]
    executed_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    batch_id: UUID | None = None


class CommandBatch(BaseModel):
    """Gruppo comandi = un passo undo."""

    batch_id: UUID
    commands: tuple[Command, ...]

    def apply(self, document: ProjectDocument) -> None:
        for command in self.commands:
            command.apply(document)

    def revert(self, document: ProjectDocument) -> None:
        for command in reversed(self.commands):
            command.revert(document)


UndoDirection = Literal["undo", "redo"]
