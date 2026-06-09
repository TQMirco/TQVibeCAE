# Tooling di sviluppo

## Requisiti

- Python 3.12+
- Git

## Setup ambiente

```powershell
cd TQVibeCAE
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
pre-commit install --hook-type pre-push
```

## Comandi frequenti

| Comando | Scopo |
|---------|---------|
| `pytest` | Suite test |
| `pytest tests/unit -q` | Unit rapidi |
| `pytest --hypothesis-profile=ci` | Property-based (profilo CI) |
| `ruff check .` | Lint |
| `ruff format .` | Format |
| `pyright` | Type check statico |
| `pre-commit run --all-files` | Tutti gli hook pre-commit |

## pre-commit

Hook pre-commit: Ruff, Pyright, igiene file.
Hook pre-push: pytest unit + profilo Hypothesis CI.

Non usare `--no-verify` salvo necessità esplicita.

Aggiornamento hook: `pre-commit autoupdate` — registrare in [dependencies.md](dependencies.md).

## Type checking

- **beartype:** runtime via `beartype_this_package()` in `tqvibecae.__init__`
- **Pyright:** config in `pyproject.toml` `[tool.pyright]`

## Test

- TDD per Model e commands
- Hypothesis per round-trip e invarianti
- Regressione bug in `tests/regression/`

Vedi regole Cursor `testing-tdd`, `linting-ruff`, `pre-commit`.
