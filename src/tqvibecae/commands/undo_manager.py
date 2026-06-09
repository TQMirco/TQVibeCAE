"""Undo/redo stack in memoria."""

from __future__ import annotations

from tqvibecae.commands.base import Command, CommandBatch


class UndoManager:
    """Gestisce stack undo e redo."""

    def __init__(self, max_depth: int = 100) -> None:
        self._max_depth = max_depth
        self._undo: list[Command | CommandBatch] = []
        self._redo: list[Command | CommandBatch] = []

    def push(self, item: Command | CommandBatch) -> None:
        self._undo.append(item)
        self._redo.clear()
        if len(self._undo) > self._max_depth:
            self._undo.pop(0)

    def undo(self, document: object) -> bool:
        from tqvibecae.model.project import ProjectDocument

        if not self._undo or not isinstance(document, ProjectDocument):
            return False
        item = self._undo.pop()
        item.revert(document)
        self._redo.append(item)
        return True

    def redo(self, document: object) -> bool:
        from tqvibecae.model.project import ProjectDocument

        if not self._redo or not isinstance(document, ProjectDocument):
            return False
        item = self._redo.pop()
        item.apply(document)
        self._undo.append(item)
        return True

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)
