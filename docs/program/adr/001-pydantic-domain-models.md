# ADR-001: Pydantic v2 per il Model di dominio

## Stato

Accettata

## Contesto

TQVibeCAE deve essere AI-first: serializzazione JSON stabile, validazione rigorosa, contratti machine-readable (JSON Schema) per automazioni e assistenza in-app.

Alternative valutate:

- `dataclass` + `to_dict()`/`from_dict()` manuali
- Solo beartype per validazione runtime
- msgspec (veloce ma ecosistema JSON Schema meno maturo per AI tooling)

## Decisione

Usare **Pydantic v2** (`BaseModel`) per:

- Entità in `src/tqvibecae/model/`
- Payload dei `Command` in `src/tqvibecae/commands/`
- DTO esposti alle query API read-only

**beartype** resta per funzioni procedurali (`CommandBus`, servizi I/O, adapter AI), non per sostituire la validazione strutturale dei modelli.

Serializzazione canonica:

- `model_dump(mode="json")`
- `model_validate(data)`

JSON Schema: `model_json_schema()` esportato in `docs/program/schemas/`.

## Conseguenze

### Positive

- JSON Schema nativo per integrazione LLM / MCP
- Validazione dichiarativa (`Field`, validator) + messaggi strutturati
- Allineamento naturale con Hypothesis (round-trip su dict JSON)
- Pyright con tipi generati/comprensibili

### Negative

- Dipendenza runtime aggiuntiva
- Overlap concettuale con beartype — mitigato dalla divisione ruoli documentata

### Neutrali

- Migrazioni schema restano esplicite (`schema_version` + funzioni dedicate)

## Alternative considerate

1. **dataclass manuale** — più boilerplate, schema AI duplicato
2. **solo beartype** — niente JSON Schema automatico, validazione meno ricca su nested models
3. **msgspec** — performance ottima, meno adatto al workflow JSON Schema + AI documentato

## Riferimenti

- Regola Cursor `domain-model.mdc`
- `docs/program/ai-integration.md`
