# Data model — open questions

**Stato:** In discussione  
**Parent:** [data-model-specification.md](data-model-specification.md)

Decisioni da chiudere in review prima di promuovere la spec ad ADR-002.

---

## 1. Sync layout ↔ schema

**Contesto:** §1 considerazioni — chi è master quando layout e schema divergono?

**Proposta attuale (spec):** `Device` master per property tecniche; geometria indipendente per fragment vs layout.

**Da decidere:**

- [ ] Modifica taglia contattore nel layout aggiorna automaticamente footprint schema o solo BOM?
- [ ] Rimozione device dallo schema rimuove anche layout placement o lo lascia orphan?
- [ ] UI: conflitto esplicito o merge silenzioso?

**Raccomandazione:** conflitti → dialog + `ValidationIssue`; default propagazione tecnica da `Device`.

---

## 2. Shard topology — monolite vs range

**Contesto:** §15 performance — progetti con migliaia di net.

**Opzioni:**

| Opzione | Pro | Contro |
|---------|-----|--------|
| A) `topology/nets.json` unico | Semplice MVP | Lento load progetti grandi |
| B) `topology/nets_{range}.json` | Lazy load | Complessità manifest |
| C) SQLite embedded nel progetto | Query veloci | Meno git-friendly |

**Raccomandazione:** A in MVP, B in v1 se benchmark lo richiedono.

---

## 3. UserWorkspaceState — globale vs per-progetto

**Contesto:** §12 — zoom ultimo foglio, layout pannelli.

**Opzioni:**

- Solo in `.tqvibe/workspace/` (per progetto)
- Globale in `%APPDATA%` + override per progetto
- Entrambi con merge

**Raccomandazione:** per-progetto in `.tqvibe/workspace/`; recenti globali in `ApplicationSettings.recent_projects`.

---

## 4. Import EPLAN — stub PartNumber

**Contesto:** articolo in export ma assente in libreria.

**Opzioni:**

- `create_stub_parts=True` → inserisce PartNumber minimale in SQLite
- Lascia `part_ref=None` + warning
- Blocca import

**Raccomandazione:** configurabile in `ImportMappingProfile`; default warning senza stub.

---

## 5. Profondità import EPLAN MVP

**Contesto:** quanto del progetto EPLAN importare nella prima release adapter.

**Scope minimo proposto:**

- Pagine + simboli + net + designation
- Escluso: layout, macro parametriche, PLC config

**Da confermare:** sufficiente per onboarding utenti da EPLAN?

---

## 6. CommandRecord audit persistito

**Contesto:** §11 undo non persistito; utile per audit e replay AI.

**Opzione futura:** log append-only opzionale `project_audit.jsonl` separato da undo stack.

**Da decidere:** day-1 o deferred?

**Raccomandazione:** deferred — solo undo in memoria in MVP.

---

## 7. Presentation refs nel project shard

**Contesto:** `WireGraphic` / `SymbolGraphic` — dove persistere coordinate canvas?

**Opzioni:**

- Dentro `sheets/{id}.json` come sottostruttura presentation
- File separato `sheets/{id}.graphics.json`

**Raccomandazione:** stesso shard sheet con sezione `graphics` — separazione logica in JSON, stesso file per coerenza undo/save.

---

## 8. Grafica AI — solo composizione da celle vs SVG libero

**Contesto:** AI potrebbe generare SVG completo invece di comporre `GraphicCellInstance`.

**Opzioni:**

| Opzione | Pro | Contro |
|---------|-----|--------|
| A) Solo composizione celle + primitive tipizzate | Validabile, riuso, coerenza IEC | Meno flessibile per simboli rari |
| B) SVG/Path import come fallback | Massima flessibilità | Difficile validazione, peggior riuso |
| C) A + conversione SVG→celle (tool offline) | Compromesso | Pipeline extra |

**Raccomandazione:** **A** in MVP; **C** opzionale v2 per import EPLAN/DXF simboli non mappati.

---

## 9. Media — blob in SQLite vs filesystem

**Contesto:** PDF datasheet possono essere grandi.

**Raccomandazione:** filesystem `{id}/file.pdf` + metadati in SQLite; mai blob grande dentro JSON progetto.

---

## Come chiudere una question

1. Discussione in review
2. Aggiornare [data-model-specification.md](data-model-specification.md)
3. Se decisione architetturale stabile → promuovere ad [ADR-002](../program/adr/) (futuro)
