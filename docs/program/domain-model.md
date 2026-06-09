# Modello dati — glossario

> Documento in evoluzione. Aggiornare ad ogni nuova entità o concetto dominio.

## Ambito

CAD **elettrico** (impianti, quadri). Non elettronica / PCB.

## Entità base (pianificate)

| Entità | Descrizione |
|--------|-------------|
| `Project` | Root documento; `schema_version`, metadati |
| `Drawing` | Foglio schema (unifilare/multifilare) |
| `SymbolInstance` | Istanza simbolo su foglio |
| `Conductor` | Conduttore semantico (sezione, identificazione filo) |
| `Connection` | Collegamento tra morsetti/nodi |
| `Terminal` | Morsetto / punto di connessione |
| `PanelBoard` | Quadro elettrico |

## Identità

- `id: UUID` immutabile per ogni entità
- `entity_type: str` per registry estensibile
- Campi semantici AI: `human_label`, `tags`, `role`

## Grafo

```
Nodi: SymbolInstance, Terminal, Bus
Archi: Connection, Conductor
```

Netlist e validazione derivano dal grafo, non dalla grafica.

## Semantica vs presentazione

| Dominio | Presentazione (View) |
|---------|----------------------|
| `Conductor` | `WireGraphic` |
| `SymbolRef` | disegno simbolo su canvas |

## Serializzazione — Pydantic v2

Tutte le entità dominio e i payload Command sono `pydantic.BaseModel`.

- JSON: `model_dump(mode="json")` / `model_validate(data)`
- JSON Schema per AI: `model_json_schema()` → file in [schemas/](schemas/)
- Modelli immutabili: `model_config = ConfigDict(frozen=True)`
- Union polimorfiche: `discriminator="entity_type"`

Vedi [adr/001-pydantic-domain-models.md](adr/001-pydantic-domain-models.md).

## Unità SI

A, V, W, mm², °C — coerenti in tutto il Model.

## Estensione

Nuovi tipi simbolo → registry `SymbolDefinition`, non fork classi base.

Vedi ADR e regola Cursor `domain-model`.
