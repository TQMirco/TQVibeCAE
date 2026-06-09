# TQVibeCAE — Guida per agent AI

CAD elettrico open source (impianti, quadri, schemi unifilari/multifilari).
**Non** è un CAD elettronico: niente PCB, SPICE, footprint SMD.

## Stack

- Python 3.12+
- PySide6 (solo View / ViewModel)
- Pydantic v2 (Model, commands, JSON/JSON Schema)
- pytest, pytest-qt, Hypothesis
- beartype (runtime su funzioni) + Pyright (statico)
- Ruff (lint + format)
- pre-commit

## Lingua

- Codice, identificatori, commenti inline: **inglese**
- Docstring Google, `docs/program/`, `docs/user manual/`: **italiano**

## Layout repository

```
src/tqvibecae/
  model/          # dominio puro, zero Qt
  viewmodel/      # QObject, segnali, orchestrazione
  view/           # widget Qt
  services/       # I/O, export, adapter AI
  commands/       # command pattern (undo/redo + automazioni)
tests/
  unit/
  integration/
  regression/
  strategies/     # strategie Hypothesis
docs/
  program/        # architettura, ADR, scelte tecniche
  user manual/    # guida operatore
.cursor/rules/    # regole Cursor (.mdc)
```

## Regole Cursor — quando consultarle

| Attività | Regola |
|----------|--------|
| Qualsiasi modifica | `core-project` |
| Model / dominio | `domain-model` |
| UI / widget | `architecture-mvvm`, `pyside6-views` |
| Test | `testing-tdd` |
| Tipi | `typing-beartype` |
| Lint/format | `linting-ruff`, `pre-commit` |
| Documentazione | `documentation-it` |
| Automazioni AI | `ai-first-design` |
| Commit | `git-commits` |
| Concetti elettrici | `electrical-cad-domain` |

## Policy progetto

- Fase embrionale: **breaking changes ammessi**; preferire correttezza e pulizia a retrocompatibilità.
- Architettura **MVVM rigida**: Model testabile senza PySide6.
- Modello dati estensibile e serializzabile (JSON) — priorità massima.
- Ogni mutazione via `commands/`; query read-only separate per AI.
- TDD per Model/commands; Hypothesis per round-trip e invarianti.
- Non committare senza richiesta esplicita dell'utente.
- Non usare `--no-verify` su pre-commit salvo richiesta esplicita.

## Setup dev (riassunto)

Vedi `docs/program/tooling.md`. In sintesi:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
pre-commit install --hook-type pre-push
```

## Documentazione

- Sviluppatori: `docs/program/`
- Operatore: `docs/user manual/`
- Nuova dipendenza: aggiornare `docs/program/dependencies.md`
