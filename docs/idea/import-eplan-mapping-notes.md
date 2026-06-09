# Note mapping import EPLAN → TQVibeCAE

**Stato:** In discussione  
**Parent:** [data-model-specification.md](data-model-specification.md)  
**Input:** export EPLAN Electric P8 (XML / intermediate export)

Documento companion con mapping campo-per-campo. Non è implementazione parser.

---

## 1. Scope import EPLAN (MVP)

| Area EPLAN | Import MVP | Note |
|------------|------------|------|
| Pagine / fogli | Sì | → `Sheet` |
| Simboli funzione | Sì | → `SchematicFragment` + `Device` |
| Connessioni / potenziali | Sì | → `Net`, `ConnectionPoint` |
| Referenze (-KM1, =+…) | Sì | → `StructuredDesignation` |
| Part number / articolo | Se presente in export | → `CatalogReference` / `PartNumber` |
| Cross-reference multipagina | Parziale | Index aggiornato; link rotti → warning |
| Layout quadro / 3D | No MVP | Warning esplicito |
| Macro EPLAN parametrizzate | No MVP | Import come gruppo statico o skip |
| Config PLC / TIA link | No MVP | — |

---

## 2. Flusso adapter

```
EPLAN export file
  → EplanImportAdapter.parse() → EplanIntermediateModel (DTO interno services)
  → EplanMappingProfile.apply() → ImportPreview (Device/Net/Sheet proposti)
  → UI review
  → CommandBatch → Project Model
  → ImportReport
```

`EplanIntermediateModel` **non** è persistito — solo DTO transitorio in `services/import/`.

---

## 3. Mapping entità principali

### 3.1 Pagina → Sheet

| EPLAN (concettuale) | TQVibeCAE | Regola |
|---------------------|-----------|--------|
| Page name | `Sheet.human_label` | Copia diretta |
| Page number | metadata sheet | Ordinamento |
| Page description | `LocalizedString.default` | IT/DE se presente |
| Page revision | `SheetRevision` | Se in export |

### 3.2 Simbolo / dispositivo → Device + SchematicFragment

| EPLAN | TQVibeCAE | Regola |
|-------|-----------|--------|
| Device tag (-KM1) | `StructuredDesignation.component_designator` | Normalizzare prefisso `-` |
| Function / location | `function_prefix`, `location_prefix` | Parsing IEC 81346 se presente |
| Symbol macro ID | lookup `SymbolDefinition` | Tabella mapping esterna `eplan_symbol_map.json` |
| Multiple symbols same device | 1 `Device`, N `SchematicFragment` | Raggruppare per device tag |
| Coil vs power contact | `SchematicFragment.fragment_role` | `coil`, `no_contact`, `nc_contact`, … |

### 3.3 Connessioni → Net

| EPLAN | TQVibeCAE | Regola |
|-------|-----------|--------|
| Connection / potential | `Net` | Una net per gruppo connesso |
| Potential name (24V+, PE) | `PotentialAssignment` | Se dichiarato |
| Wire / cable ref | `Cable` + `Core` | Se export include cable data |
| Single wire | `Cable` con 1 `Core` | Modello unificato |

### 3.4 Articolo commerciale → CatalogReference

| EPLAN | TQVibeCAE | Regola |
|-------|-----------|--------|
| Part number | `PartNumber` in libreria o ref | Match libreria locale |
| Manufacturer | campo costruttore | Import catalogo se assente |
| Order number | `PartNumber` | — |

Se articolo non in libreria: creare `PartNumber` stub in libreria **o** lasciare `part_ref=None` con warning (configurabile in `ImportMappingProfile`).

---

## 4. Tabella mapping simboli (esempio stub)

File futuro: `resources/import/eplan_symbol_map.json`

| eplan_macro_id | tqvibecae_symbol_definition_id | note |
|----------------|-------------------------------|------|
| `IEC_MOTOR_001` | UUID… | Motore |
| `IEC_CONTACTOR_COIL` | UUID… | Bobina |
| `IEC_CONTACTOR_NO` | UUID… | Contatto NA |
| `IEC_BREAKER_1P` | UUID… | Interruttore |

Simbolo non mappato → `UnmappedExternalRef` in `ImportReport`; fragment **non** inserito finché utente non sceglie sostituto.

### Grafica componibile (EPLAN → celle)

Macro EPLAN spesso corrispondono a **composizioni** di primitive IEC, non a un blocco monolitico. Mapping preferito:

| EPLAN | TQVibeCAE |
|-------|-----------|
| Macro contatto NA singolo | `GraphicCellDefinition` `contact_no` |
| Macro interruttore 3P | `SymbolGraphicComposition` con 3× `GraphicCellInstance(contact_no)` |
| Simbolo non decomponibile | v2: conversione offline SVG→celle, o placeholder |

Tabella estesa futura: `resources/import/eplan_graphic_cell_map.json` (oltre a `eplan_symbol_map.json`).

---

## 5. Referenze e cross-ref

| Caso | Comportamento |
|------|---------------|
| Cross-ref valido multipagina | `ProjectIndex` aggiornato device→sheets |
| Target mancante nell'export | Warning `CROSS_REF_UNRESOLVED` |
| Referenza duplicata | Errore validazione; utente risolve in preview |

---

## 6. ImportMappingProfile

```python
class ImportMappingProfile(BaseModel):
    id: UUID
    name: str
    symbol_map_path: str | None
    create_stub_parts: bool = False
    merge_devices_by_tag: bool = True
    default_reference_standard: Literal["IEC", "NFPA"] = "IEC"
    on_unmapped_symbol: Literal["skip", "placeholder", "fail"] = "skip"
```

Profili predefiniti: `eplan_default_iec`, `eplan_strict`.

---

## 7. Codici warning / errori import

| Code | Severità | Descrizione |
|------|----------|-------------|
| `EPLAN_SYMBOL_UNMAPPED` | warning | Simbolo senza mapping |
| `EPLAN_PART_NOT_IN_LIBRARY` | warning | Articolo non trovato |
| `EPLAN_CROSS_REF_UNRESOLVED` | warning | Cross-ref rotto |
| `EPLAN_LAYOUT_SKIPPED` | info | Layout non importato (MVP) |
| `EPLAN_DUPLICATE_DESIGNATION` | error | Tag duplicato incompatibile |

---

## 8. Limiti noti

- Export EPLAN varia per versione P8 e opzioni export — adapter deve dichiarare `supported_export_versions`.
- Nessuna garanzia round-trip EPLAN ↔ TQVibeCAE in MVP.
- DXF export EPLAN: usare `DxfImportAdapter` separato (solo geometria).

---

## Riferimenti

- [data-model-specification.md](data-model-specification.md) — sezione 16 Import
- [electrical-cad-design-considerations.md](electrical-cad-design-considerations.md) — §17
