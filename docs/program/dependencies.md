# Dipendenze

Aggiornare questo file ad ogni nuova dipendenza runtime o dev.

## Runtime

| Pacchetto | Versione | Motivo |
|-----------|----------|--------|
| PySide6 | >=6.6 | GUI Qt |
| pydantic | >=2.0 | Model dominio, JSON, JSON Schema per AI |
| beartype | >=0.18 | Type checking runtime su funzioni/servizi |

## Sviluppo

| Pacchetto | Versione | Motivo |
|-----------|----------|--------|
| pytest | >=8.0 | Test |
| pytest-qt | >=4.4 | Test integrazione Qt |
| hypothesis | >=6.100 | Property-based testing |
| pyright | >=1.1.380 | Type check statico |
| ruff | >=0.8 | Lint + format |
| pre-commit | >=4.0 | Git hooks |

## pre-commit hook repos

| Repo | Rev | Note |
|------|-----|------|
| pre-commit-hooks | v5.0.0 | Igiene file |
| ruff-pre-commit | v0.8.4 | Lint/format |
| local pyright | system | Type check |
| local pytest | system | pre-push |

Ultimo `pre-commit autoupdate`: _(non ancora eseguito)_
