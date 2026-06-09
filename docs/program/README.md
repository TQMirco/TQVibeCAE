# Documentazione sviluppatori — TQVibeCAE

Indice della documentazione tecnica del progetto (lingua: **italiano**).

## Indice

| Documento | Contenuto |
|-----------|-----------|
| [architecture.md](architecture.md) | Panoramica architetturale |
| [mvvm-layers.md](mvvm-layers.md) | Model, ViewModel, View — responsabilità |
| [domain-model.md](domain-model.md) | Glossario entità e grafo elettrico |
| [ai-integration.md](ai-integration.md) | Command bus, query API, schema JSON |
| [tooling.md](tooling.md) | Setup dev, pytest, Ruff, pre-commit |
| [dependencies.md](dependencies.md) | Dipendenze runtime e dev |
| [adr/001-pydantic-domain-models.md](adr/001-pydantic-domain-models.md) | Pydantic v2 per Model e JSON Schema |

## Schema JSON

Contratti machine-readable in [schemas/](schemas/).

## Regole Cursor

Convenzioni per agent AI in `.cursor/rules/` — vedi anche `AGENTS.md` alla root.
