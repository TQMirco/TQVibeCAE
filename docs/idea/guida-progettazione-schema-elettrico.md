# Guida alla progettazione dello schema elettrico

**Stato:** Bozza  
**Pubblico:** progettisti impiantistici, revisori documentazione, sviluppatori TQVibeCAE che devono allineare validazioni e UX alle pratiche di settore.

Documento di **riferimento didattico** su come si legge, si progetta e si revisiona uno schema elettrico di impianto (quadri, macchine, cablaggio industriale). Non sostituisce le norme ufficiali né le istruzioni del committente: indica **cosa dicono le normative rilevanti**, **quali convenzioni adottare** e **come strutturare un buono schema**.

**Relazione con altri documenti:**

| Documento | Ruolo |
|-----------|-------|
| [electrical-cad-design-considerations.md](electrical-cad-design-considerations.md) | Trappole di dominio per il **software** (data model, ERC, sync layout) |
| Questo documento | Buone pratiche per il **progettista** e requisiti che TQVibeCAE dovrà supportare |
| [data-model-specification.md](data-model-specification.md) | Come il modello dati traduce convenzioni e entità |
| [`docs/user manual/`](../user%20manual/) | Workflow operativo dell'applicazione (quando rilasciato) |

> **Disclaimer:** citazioni normative sintetiche a scopo guida. Per conformità formale consultare sempre il testo ufficiale aggiornato (CEI, IEC, UNI) e le specifiche contrattuali del progetto.

---

## 1. Normative e documenti di riferimento

### 1.1 Panoramica per ambito

| Ambito | Norma / documento | Cosa regola |
|--------|-------------------|-------------|
| Simboli grafici | **IEC 60617** (database online); in Italia **CEI 3-7** | Forma e significato dei simboli su schema |
| Documentazione | **IEC 61082** ser.; **CEI 3-13** | Tipi di documento, cartiglio, struttura fogli, riferimenti incrociati |
| Designazione | **IEC 81346** ser.; **CEI EN 81346** | Identificazione strutturata di sistemi, oggetti e segni |
| Colori conduttori | **IEC 60445**; **HD 308 S2**; **CEI 64-8** (cap. su identificazione) | Colori funzionali (L, N, PE, DC, segnali) |
| Codici colore | **IEC 60757** | Abbreviazioni (BK, BU, GNYE, RD, …) per etichette e distinte |
| Impianti BT utilizzatori | **CEI 64-8** | Requisiti impiantistici (non è uno «schema type», ma vincola sezioni, protezioni, PE) |
| Macchine elettriche | **EN 60204-1** | Documentazione elettrica macchina, sicurezza, schema quadro comando |
| Cablaggio quadri | **IEC 61439** ser. | Assemblaggio quadri BT (verifica, non disegno simbolico) |
| Etichettatura | **IEC 62275**; prassi costruttori | Identificazione fili, morsetti, componenti |

TQVibeCAE è orientato a **IEC/CEI** (impiantistica europea). Progetti **NFPA** (Nord America) usano simbologia e flussi diversi: vanno impostati a livello progetto, non mescolati nello stesso documento.

### 1.2 Cosa «obbliga» la norma vs cosa è convenzione aziendale

Le norme definiscono in genere:

- **Simboli** ammessi e loro significato funzionale
- **Informazioni minime** che un documento deve contenere (designazione, tensione, potenza dove rilevante)
- **Regole di identificazione** (81346) se adottate contrattualmente
- **Colori** obbligatori per conduttori di sistema (PE, neutro in AC, polarità DC)

Non definiscono (o definiscono solo parzialmente):

- Ordine esatto dei fogli nel fascicolo
- Griglia millimetrica del foglio
- Densità massima di simboli per area
- Schema di numerazione fili interno al cantiere (sequenziale, per potenziale, per morsetto destinazione)

Queste ultime sono **best practice** o **standard di committente** (automotive, oil & gas, utility) che il CAD deve poter configurare per progetto — vedi [data-model-specification.md §8](data-model-specification.md).

### 1.3 Tipi di documento (IEC 61082)

Conoscere la tipologia evita di disegnare «tutto su un foglio»:

| Tipo | Scopo | Contenuto tipico |
|------|-------|------------------|
| Schema **unifilare** | Vista d'insieme rete | Linee, trasformatori, quadri, protezioni principali |
| Schema **multifilare** / **a multifili** | Logica di comando e protezione | Contatti, bobine, relè, interlock |
| Schema **di principio** | Funzione elettrica | Simboli funzionali, poche info costruttive |
| Schema **di collegamento** | Collegamento tra apparati | Morsetti, connettori, riferimenti cavo |
| Schema **cablaggio** / **wire list** | Realizzazione | Percorsi, lunghezze, etichette capocorda |
| Layout **quadro** | Montaggio fisico | Posizione su guida DIN, ingombri |

Un **buon fascicolo** separa i livelli: lo schema multifilare non sostituisce il layout quadro né la distinta cavi.

---

## 2. Principi di un buono schema multifilare

### 2.1 Flusso di lettura

Convenzione più diffusa in ambito IEC (non obbligatoria ma facilita la revisione):

```
Alimentazione / ingresso energia          Carico / uscita verso campo
        ← sinistra                              destra →
        ↑ alto = tensione più elevata (es. L1, L2, L3)
        ↓ basso = ritorno, neutro, 0 V, PE (often in basso o su rail dedicati)
```

Segnali di comando (24 V DC, PLC) spesso su zone centrali o fogli dedicati, con **alimentazione simbolica** (continuità tra fogli) esplicita.

### 2.2 Leggibilità

| Principio | Perché |
|-----------|--------|
| **Una funzione per area** | Es. un foglio «Avviamento motore M1», un foglio «Illuminazione piano 2» |
| **Rail di alimentazione continui** | Bus L/N/PE/24V tracciati come linee orizzontali; derivazioni verticali |
| **Spaziatura uniforme** | Griglia (es. 2,5 mm o 5 mm); simboli allineati |
| **Evitare di incrociare fili** | Usare ponti, giro filo o secondo foglio; incroci senza nodo = ambiguità |
| **Testo orizzontabile** | Referenze componenti leggibili senza ruotare il foglio |
| **Stato normale indicato** | Contatti NA/NC nello stato a riposo (bobina non eccitata, ecc.) |

### 2.3 Completezza informativa minima

Su ogni componente rilevante:

- **Designazione** (es. `-KM1`, `=SYS+LOC-KM1` se 81346)
- **Tipo/funzione** deducibile dal simbolo o da nota
- **Parametri** quando non impliciti: tensione bobina, corrente nominale interruttore, range termico
- **Collegamento a terra** dove richiesto (simbolo PE, morsetti di passaggio)

Su ogni filo (multifilare di cablaggio):

- **Identificativo** univoco nel progetto (o per potenziale, se schema lo prevede)
- **Sezione** e, per cavi multipolari, **riferimento cavo** (W1, W2)

---

## 3. Designazione componenti (IEC 81346)

### 3.1 Prefissi funzione comuni (IEC 81346-2)

| Prefisso | Funzione | Esempi |
|----------|----------|--------|
| `-Q` | Apparecchi di manovra/protezione | `-Q1` interruttore, `-QF3` magnetotermico |
| `-F` | Protezione sovracorrente | `-F1` fusibile |
| `-K` | Relè, contattori | `-KM1` contattore, `-KA1` relè ausiliario |
| `-S` | Commutatori, sezionatori | `-S1` selettore |
| `-H` | Segnalazione | `-HL1` spia |
| `-M` | Motori | `-M1` |
| `-T` | Trasformatori | `-T1` |
| `-X` | Morsetti, connettori | `-X1` morsettiera |

Il prefisso descrive la **funzione**, non il costruttore. Il codice articolo sta in distinta/BOM, non sostituisce la designazione schematica — vedi [electrical-cad-design-considerations.md §7](electrical-cad-design-considerations.md).

### 3.2 Struttura gerarchica

Forma completa (quando richiesta dal committente):

```
=FUNZIONE +LOCazione -Componente :Terminale
```

Esempio: `=CONV1 +CP01 -KM1` — contattore KM1 del quadro CP01 del trasportatore CONV1.

**Best practice:**

- Definire regole **a inizio progetto** (numerazione globale vs per macchina vs per foglio)
- Non riutilizzare la stessa designazione per device diversi
- Usare **riferimenti incrociati** (vedi §5) quando bobina e contatti di potenza sono su fogli diversi

---

## 4. Conduttori, colori e cavi

### 4.1 Colori funzionali (sintesi IEC 60445 / prassi impianti BT)

| Conduttore | Colore tipico (AC) | Codice IEC 60757 |
|------------|-------------------|------------------|
| Fase L1 | Marrone | BN |
| Fase L2 | Nero | BK |
| Fase L3 | Grigio | GY |
| Neutro N | Azzurro chiaro | BU |
| Terra PE | Giallo/verde | GNYE |
| DC + | Rosso (o rosso/marrone per polarità) | RD |
| DC − | Nero o blu scuro | BK / BU |

In impianti esistenti o export verso paesi diversi verificare sempre il profilo normativo del progetto.

### 4.2 Sezione e tipo

- La **sezione (mm²)** deve essere coerente con protezione a monte e corrente di esercizio (CEI 64-8, tabelle correnti ammissibili).
- Distinguere **filo unipolare** da **cavo multipolare** con riferimento W: le anime condividono percorso fisico ma possono appartenere a net diverse.
- Documentare **pin non usati** su connettori (NC — not connected), non lasciarli ambigui.

### 4.3 Numerazione fili — schemi comuni

| Metodo | Quando usarlo | Esempio |
|--------|---------------|---------|
| Sequenziale per progetto | Cablaggio officina, etichettatrice | 001, 002, 003… |
| Per potenziale | Controllo PLC, stesso 24V+ su più fili | Tutti i ritorni «0V» con stesso id logico |
| Destinazione morsetto | Norma DIN / abitudine germanica | Numero = morsetto di arrivo |
| Per cavo | Multipolari | W4-1, W4-2, W4-3 (cavo W4, anima 1…) |

Il CAD deve applicare **una regola configurabile**, non imporsi un solo stile — vedi considerazioni §8.

---

## 5. Riferimenti incrociati e continuità tra fogli

Quando un componente è **spezzato** su più fogli (bobina su foglio 5, contatti su foglio 6):

1. Ogni fragment porta la **stessa designazione** (`-KM1`).
2. Si usa un simbolo o nota di **riferimento incrociato**: es. «Vedi foglio 6, riga 4» / «Contatti potenza → /S6».
3. Le **net globali** (PE, N, barre 24 V) possono propagarsi senza simbolo su ogni foglio se definito nelle impostazioni progetto; altrimenti usare **simboli di continuità** espliciti.

**Errore frequente:** bobina `-KM1` su un foglio e contatti etichettati `-KM2` per errore — rompe BOM, wire list e diagnostica sul campo.

---

## 6. Best practice per famiglie di componenti

### 6.1 Contattori e relè

- **Bobina** con tensione nominale indicata (230 V AC, 24 V DC).
- **Contatti di potenza** separati dagli **ausiliari**; mostrare tutti i blocchi montati (NA/NC aggiuntivi).
- Stato a riposo: contatti NA aperti, NC chiusi.
- Collegare **suppressione bobina** (RC, diodo) se prevista — può essere nota o parametro device.

### 6.2 Interruttori, magnetotermici, differenziali

- Curva (**B, C, D**), corrente nominale **In**, potere di interruzione se rilevante.
- Differenziale: sensibilità **IΔn** (30 mA, 300 mA…).
- Posizione su schema: in genere a monte del circuito protetto, flusso sinistra → destra.

### 6.3 Morsettiere

- Numerazione morsetti **coerente** con planimetria quadro e etichette fisiche.
- Morsetto **doppio livello**: due simboli schematici, **un** componente fisico in BOM (trappola §6 considerazioni).
- **Ponticelli** (jumper): cambiano topologia elettrica senza filo visibile — vanno modellati esplicitamente.

### 6.4 Motori, inverter, PLC

- Motore: `-M1`, collegamento morsetti (U/V/W, PE) allineato al datasheet.
- Inverter: separare **potenza** e **controllo**; morsetti digitali/analogici con riferimento al manuale.
- PLC: I/O numerati come sul modulo fisico; **tag** software opzionali in nota, non sostituiscono designazione hardware.

### 6.5 Connettori di campo

- Coppia **plug/socket** (XP/XS) con pin mapping speculare.
- Indicare **cavo di collegamento** (tipo, schermo, continuità schermo a un solo capo se applicabile).

---

## 7. Revisione, cartiglio e tracciabilità

Allineato a IEC 61082 e prassi industriale:

| Elemento | Pratica corretta |
|----------|------------------|
| **Cartiglio** | Titolo foglio, numero foglio, revisione foglio, scala, norma simboli |
| **Revisione foglio** | A, B, C… ad ogni modifica tecnica approvata |
| **Emissione progetto** | 00, 01… al rilascio formale (congela baseline) |
| **Revision cloud** | Evidenziare aree modificate tra revisioni (settori regolamentati) |
| **Stato approvazione** | Foglio «issued» non modificabile senza incremento revisione |

Dettaglio implicazioni software: [electrical-cad-design-considerations.md §10](electrical-cad-design-considerations.md).

---

## 8. Checklist qualità schema

Usare prima dell'emissione (manuale o automatizzata con ERC):

### 8.1 Struttura e documentazione

- [ ] Tipologia documento corretta (multifilare vs unifilare vs layout)
- [ ] Indice fogli e numerazione progressiva
- [ ] Cartiglio completo su ogni foglio
- [ ] Norma simboli indicata (IEC/CEI)

### 8.2 Designazione e coerenza

- [ ] Designazioni univoche nel progetto
- [ ] Prefissi funzione conformi alle regole progetto / 81346
- [ ] Riferimenti incrociati risolti (nessun «Vedi foglio ??» placeholder)
- [ ] Fragment dello stesso device con stessa tag (`-KM1` ovunque)

### 8.3 Elettrico e cablaggio

- [ ] Ogni connessione è una net esplicita (no fili «quasi toccati»)
- [ ] PE continuo dove richiesto
- [ ] Sezioni fili definite o derivabili da regole
- [ ] Colori / tipo conduttore coerenti con potenziale
- [ ] Protezione a monte compatibile con carico a valle
- [ ] Pin connettori non flottanti (usati o marcati NC)

### 8.4 Produzione

- [ ] BOM allineata a quantità fisiche (teste pulsante + blocchi contatto, non solo «1 pulsante»)
- [ ] Wire list generabile senza campi vuoti obbligiori
- [ ] Layout quadro sincronizzato (posizione componenti ↔ schema)

---

## 9. Tutorial — avviamento diretto motore (schema multifilare)

Esempio didattico minimo: motore `-M1` avviato da contattore `-KM1`, protezione `-QF1`, comando Start/Stop.

### 9.1 Struttura fogli suggerita

| Foglio | Contenuto |
|--------|-----------|
| S1 | Rete e potenza: `-QF1`, `-KM1` (contatti potenza), `-M1`, PE |
| S2 | Comando: pulsanti Start/Stop, bobina `-KM1`, contatto aux NA in parallelo a Start |

### 9.2 Passi di disegno

1. **Impostare progetto**: norma IEC, griglia 5 mm, schema numerazione fili sequenziale.
2. **Foglio S1 — rail potenza**: tracciare bus L1/L2/L3 (o monofase L/N) in alto; PE in basso.
3. Inserire `-QF1` (magnetotermico motore) sul conduttore di fase; parametri: In secondo motore.
4. Inserire `-KM1` contatti potenza tra `-QF1` e `-M1`; collegare `-M1` a PE.
5. **Foglio S2 — comando**: alimentazione 24 V DC (o 230 V se comando diretto) con rail +/−.
6. Pulsante Stop (NC) in serie a pulsante Start (NA); bobina `-KM1` verso 0 V.
7. Contatto aux NA di `-KM1` in parallelo a Start (autolatch).
8. Etichettare fili; riferimento incrociato bobina ↔ contatti: «-KM1 potenza → S1».
9. **ERC**: verificare bobina eccitata, nessuna net orphan, designazioni univoche.
10. **Report**: estrarre BOM (`-QF1`, `-KM1`, pulsanti, morsetti) e wire list.

### 9.3 Estensioni tipiche (esercizio)

- Aggiungere **segnalazione guasto** termico sul relè termico `-FR1` in serie alla bobina.
- Aggiungere **interblocco** con secondo motore.
- Duplicare come **macro** parametrica (In motore → dimensionamento `-QF1`).

---

## 10. Errori comuni da evitare

| Errore | Conseguenza | Remedy |
|--------|-------------|--------|
| Mescolare simbologia IEC e NFPA nello stesso progetto | Revisioni respinte, confusione cantiere | Profilo norma a livello progetto |
| Designazione ≠ tra bobina e contatti | Cablaggio errato | Un `Device`, N `SchematicFragment` coerenti |
| Filo senza sezione su circuito potenza | Non conformità, rischio termico | Default per tipo + override per filo |
| Troppi simboli per foglio | Illeggibile in stampa A3/A4 | Suddividere per funzione/macchina |
| Net globali implicite non dichiarate | ERC falsi positivi/negativi | Configurare PE, N, 24V come globali |
| BOM «1 contattore» senza accessori | Ordine materiali incompleto | Modellare subcomponenti (blocchi aux) |
| Modifiche su foglio già «issued» senza revisione | Audit trail invalido | Workflow revisione obbligatorio |

---

## 11. Tips operativi (CAD e cantiere)

1. **Progettare dal quadro verso il campo** (alimentazione → protezione → comando → carico) riduce ripensamenti su sezioni cavo.
2. **Allineare numeri morsettiera** tra schema, layout e etichette stampate prima del cablaggio.
3. **Foglio unifilare** aggiornato per ogni modifica strutturale al quadro — serve al committente che non legge il multifilare.
4. **Libreria simboli** con varianti IEC ufficiali, non disegni «artigianali» divergenti dal database CEI 3-7 / IEC 60617.
5. **Parametrizzare macro** (avviamenti, sequenze luci) invece di copiare-incollare: una correzione si propaga.
6. **Validare early** con ERC (net orphan, PE, tensione bobina vs alimentazione comando).
7. **Documentare eccezioni** (pin NC, ponticelli, fili schermati con continuità solo a quadro) con note esplicite, non solo colore.
8. **Export verificabile**: wire list e BOM devono essere coerenti con lo schema — stessa fonte dati (modello TQVibeCAE), non spreadsheet parallelo.

---

## 12. Implicazioni per TQVibeCAE (roadmap documentazione)

Quando le funzionalità saranno rilasciate, promuovere in [`docs/user manual/`](../user%20manual/):

| Contenuto guida | Capitolo manuale target |
|-----------------|-------------------------|
| Tutorial avviamento diretto | `simboli-e-collegamenti.md` (workflow) |
| Scelta norma e numerazione | `progetto-e-schema.md` |
| Checklist ERC | `simboli-e-collegamenti.md` § Validazione |
| 81346 e riferimenti incrociati | Nuovo capitolo «Designazione e fascicolo» |

Validazioni automatiche da allineare a questa guida (non exhaustive): designazione univoca, coerenza fragment/device, colore vs potenziale, sezione vs In protezione, riferimenti incrociati risolti, stato revisione foglio.

---

## 13. Riferimenti e letture consigliate

- IEC 60617 — Graphical symbols for diagrams ([database online IEC](https://webstore.iec.ch/en/publication/607/))
- IEC 81346-1 / -2 — Industrial systems, structured designation
- IEC 61082-1 — Preparation of documents used in electrotechnology
- IEC 60445 — Basic and safety principles for conductor identification
- CEI 64-8 — Impianti elettrici utilizzatori a tensione nominale ≤ 1000 V AC
- CEI 3-7 / CEI 3-13 — Adozioni italiane simboli e documentazione
- EN 60204-1 — Safety of machinery — Electrical equipment of machines

Documentazione interna: [README idea](README.md), [import-eplan-mapping-notes.md](import-eplan-mapping-notes.md) (profili normativi import).

---

*Ultimo aggiornamento: 2025-06 — bozza iniziale.*
