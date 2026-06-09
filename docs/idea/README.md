# Idea — proposte, discussioni e sviluppi futuri

Cartella per tutto ciò che **non è ancora integrato** nel prodotto o nella documentazione ufficiale.

## Cosa va qui

| Tipo | Esempi |
|------|--------|
| **Nuovi sviluppi** (non ancora in codice) | Bozze di feature, requisiti preliminari, mock di flussi |
| **Discussioni generali** | Trade-off non decisi, domande aperte, confronto approcci |
| **Cose non integrate** | Spec scritte ma non implementate, spike abbandonati da rivalutare |
| **Idee in generale** | Wishlist, brainstorming, note da riunioni, feedback utenti |

**Lingua:** italiano (come il resto della documentazione non-code).

## Indice documenti

| Documento | Contenuto |
|-----------|-----------|
| [electrical-cad-design-considerations.md](electrical-cad-design-considerations.md) | Casistiche e trappole di dominio (17 sezioni) |
| [data-model-specification.md](data-model-specification.md) | Specifica data model — entità, persistenza, undo, settings, import, **grafica componibile §5.1**, **media §5.2** |
| [import-eplan-mapping-notes.md](import-eplan-mapping-notes.md) | Mapping EPLAN → modello TQVibeCAE |
| [data-model-open-questions.md](data-model-open-questions.md) | Decisioni aperte da review |

## Cosa non va qui

| Contenuto | Dove metterlo |
|-----------|---------------|
| Architettura **decisa** e in vigore | [`docs/program/`](../program/) — eventualmente ADR in `adr/` |
| Funzionalità **già rilasciata** per l'operatore | [`docs/user manual/`](../user%20manual/) |
| Contratto API nel codice | Docstring Google nei moduli Python |
| Bug verificati | Test in `tests/regression/` + fix nel codice |

Quando un'idea viene **accettata e implementata**, spostare o riassumere il contenuto pertinente in `docs/program/` o `docs/user manual/` e lasciare in `idea/` un breve link o nota «promossa → ADR-NNN / architettura».

## Come scrivere un documento

1. Creare un file markdown con nome descrittivo: `esportazione-pdf.md`, `libreria-simboli-iec.md`
2. In testa, indicare **stato**: `Bozza` | `In discussione` | `Accettata (non implementata)` | `Scartata` | `Promossa`
3. Descrivere contesto, obiettivo, alternative e open point — senza vincoli di template rigido
4. Opzionale: data e autore in fondo

## Regola per agent e sviluppatori

Tutte le richieste di documentazione relative a:

- nuovi sviluppi non ancora nel codice;
- discussioni generali su funzionalità o architettura **non ancora integrate**;
- idee, ipotesi, esplorazioni;

vanno create o aggiornate **in `docs/idea/`**, non in `docs/program/` (salvo promozione formale ad ADR) né nel manuale utente.

## Collegamenti

- Documentazione tecnica integrata: [`docs/program/`](../program/)
- Manuale operatore: [`docs/user manual/`](../user%20manual/)
- Template ADR (decisioni prese): [`docs/program/adr/000-template.md`](../program/adr/000-template.md)
