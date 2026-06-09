"""CommandBus — execute, undo, redo."""

from __future__ import annotations

from beartype import beartype

from tqvibecae.commands.base import Command, CommandBatch, CommandRecord
from tqvibecae.commands.undo_manager import UndoManager
from tqvibecae.model.project import ProjectDocument
from tqvibecae.model.settings import ApplicationSettings


class CommandBus:
    """Orchestrazione mutazioni con undo stack."""

    def __init__(
        self,
        document: ProjectDocument,
        settings: ApplicationSettings | None = None,
    ) -> None:
        self._document = document
        self._undo = UndoManager(
            max_depth=(settings or ApplicationSettings()).undo_max_depth
        )

    @property
    def document(self) -> ProjectDocument:
        return self._document

    @property
    def can_undo(self) -> bool:
        return self._undo.can_undo

    @property
    def can_redo(self) -> bool:
        return self._undo.can_redo

    @beartype
    def execute(self, command: Command | CommandBatch) -> CommandRecord:
        command.apply(self._document)
        self._undo.push(command)
        if isinstance(command, CommandBatch):
            return CommandRecord(
                command_type="batch",
                payload={"batch_id": str(command.batch_id)},
            )
        return CommandRecord(
            command_type=command.command_type,
            payload=command.model_dump(mode="json"),
        )

    @beartype
    def undo(self) -> bool:
        return self._undo.undo(self._document)

    @beartype
    def redo(self) -> bool:
        return self._undo.redo(self._document)
