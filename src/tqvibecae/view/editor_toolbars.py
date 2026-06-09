"""Toolbar orizzontali editor — Standard e Vista."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QLabel, QMainWindow, QToolBar


@dataclass(frozen=True, slots=True)
class EditorToolbars:
    """Barre strumenti registrate."""

    standard: QToolBar
    view: QToolBar
    undo_action: QAction
    redo_action: QAction
    save_action: QAction
    fit_action: QAction
    zoom_in_action: QAction
    zoom_out_action: QAction
    zoom_label: QLabel


def build_editor_toolbars(window: QMainWindow) -> EditorToolbars:
    """Crea barre Standard e Vista."""
    standard = QToolBar("Standard", window)
    standard.setObjectName("StandardToolBar")
    standard.setMovable(False)
    window.addToolBar(standard)

    undo_action = QAction("Annulla", window)
    undo_action.setShortcut(QKeySequence.StandardKey.Undo)
    standard.addAction(undo_action)

    redo_action = QAction("Ripeti", window)
    redo_action.setShortcut(QKeySequence.StandardKey.Redo)
    standard.addAction(redo_action)

    standard.addSeparator()
    save_action = QAction("Salva", window)
    save_action.setEnabled(False)
    save_action.setToolTip("Prossima versione")
    standard.addAction(save_action)

    view = QToolBar("Vista", window)
    view.setObjectName("ViewToolBar")
    view.setMovable(False)
    window.addToolBar(view)

    fit_action = QAction("Adatta", window)
    view.addAction(fit_action)

    zoom_in_action = QAction("Zoom +", window)
    view.addAction(zoom_in_action)

    zoom_out_action = QAction("Zoom -", window)
    view.addAction(zoom_out_action)

    zoom_label = QLabel(" 100% ")
    view.addWidget(zoom_label)

    return EditorToolbars(
        standard=standard,
        view=view,
        undo_action=undo_action,
        redo_action=redo_action,
        save_action=save_action,
        fit_action=fit_action,
        zoom_in_action=zoom_in_action,
        zoom_out_action=zoom_out_action,
        zoom_label=zoom_label,
    )
