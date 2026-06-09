# Integrazione AI

## Obiettivo

Permettere automazioni complete e assistenza in-app senza simulare click GUI.

## Mutazioni — Command bus

Ogni modifica stato passa da `Command` serializzabile:

- `command_type`, `payload`, `timestamp`
- Esecuzione: `CommandBus.execute(command)`
- Undo/redo: stack comandi

La UI e un agent AI usano lo **stesso** percorso.

## Query — Read API

Funzioni pure, output JSON stabile:

- `get_project_summary`
- `list_symbols`
- `validate_project`

Nessun side effect.

## Schema — Pydantic JSON Schema

Generare da codice, non scrivere schema a mano separati dal Model:

```python
schema = Project.model_json_schema()
# esportare in docs/program/schemas/project.schema.json
```

Gli adapter AI (`services/ai/`) consumano questi schema per function calling / structured output.
Allineati a `model_dump(mode="json")`.

## Identificatori semantici

Oltre UUID: `human_label`, `tags`, `role` per prompt e automazioni.

## Event log (futuro)

Log append-only opzionale per audit e replay.

## Adapter

`services/ai/` — LLM, MCP, ecc. Non importa View.

Vedi regola Cursor `ai-first-design`.
