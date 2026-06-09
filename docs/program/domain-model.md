# Modello dati — glossario

> Documento in evoluzione. Aggiornare ad ogni nuova entità o concetto dominio.

## Ambito

CAD **elettrico** (impianti, quadri). Non elettronica / PCB.

## Entità implementate (MVP)

| Entità | Descrizione |
|--------|-------------|
| `Project` / `ProjectDocument` | Root progetto e container in-memory |
| `ProjectIndex` | Indice denormalizzato device/net/designation |
| `ProjectManifest` | Contratto manifest `.tqvibe/` |
| `Sheet` | Foglio schema |
| `Device` / `SubComponent` | Identità canonica e parti fisiche |
| `SchematicFragment` | Apparizione device su foglio |
| `ConnectionPoint` / `Net` | Grafo topologico |
| `Cable` / `Core` | Cavi e anime |
| `PotentialAssignment` / `GlobalNetDeclaration` | Potenziali |
| `SymbolGraphic` / `PlacedSymbol` | Presentation simbolo |
| `WireGraphic` / `WireSegment` | Presentation filo canvas |
| `SheetPresentation` | Stato grafico foglio |
| `GraphicCellDefinition` / `SymbolGraphicComposition` | Grafica componibile |
| `SymbolDefinition` / `ComponentDefinition` / `PartNumber` / `FootprintDefinition` | Catalogo libreria |
| `ApplicationSettings` / `UserWorkspaceState` / `NumberingScheme` | Settings 3 livelli |
| `Command` / `CommandBus` / `UndoManager` | Sessione undo |

## Semantica vs presentazione

| Dominio | Presentation |
|---------|--------------|
| `Device` + `ConnectionPoint` | `PlacedSymbol` + pin canvas |
| `Net` | `WireGraphic` (disegno) |
| `Cable` / `Core` | futuro `WireGraphic` multisegmento |

## Grafo

```
Nodi: Device, ConnectionPoint, Terminal (v1)
Archi: Net, Cable/Core
```

## Serializzazione

Pydantic v2 — `model_dump(mode="json")` / JSON Schema in [`schemas/`](schemas/).

Vedi [adr/001-pydantic-domain-models.md](adr/001-pydantic-domain-models.md).

## Catalogo IEC editor

Categorie palette: protection, switching, control, loads, terminals, reference, measurement, transformers — vedi `resources/iec_catalog/`.

Geometria simboli allineata a **IEC 60617** / **CEI 3-7** (contatti in stato a riposo, bobina rettangolare, motore U/V/W+PE, terra PE, ecc.) — riferimento [`guida-progettazione-schema-elettrico.md`](../idea/guida-progettazione-schema-elettrico.md).
