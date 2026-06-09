# Architettura TQVibeCAE

> Documento in evoluzione — fase embrionale del progetto.

## Obiettivo

CAD elettrico open source per impianti e quadri: schemi unifilari/multifilari, simbologia IEC/CEI.

## Pattern

**MVVM rigido** con PySide6:

| Layer | Path | Qt |
|-------|------|-----|
| Model | `src/tqvibecae/model/` | No |
| ViewModel | `src/tqvibecae/viewmodel/` | QObject, Signal |
| View | `src/tqvibecae/view/` | Widget |
| Commands | `src/tqvibecae/commands/` | No |
| Services | `src/tqvibecae/services/` | No (salvo adapter espliciti) |

## Flusso dati

```
Utente → View → ViewModel → CommandBus → Model
Model → eventi dominio → ViewModel → View (aggiornamento UI)
AI → CommandBus / query API → Model
```

## Principi

1. **Model first** — estensibile, serializzabile, testabile senza GUI
2. **AI-first** — ogni mutazione via Command serializzabile
3. **Breaking changes ammessi** — correttezza > retrocompatibilità
4. Dettaglio layer: [mvvm-layers.md](mvvm-layers.md)
5. Dettaglio dominio: [domain-model.md](domain-model.md)

## ADR

Decisioni architetturali significative in [adr/](adr/).
