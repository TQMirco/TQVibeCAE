# Considerazioni di Progettazione — CAD Elettrico

Documento di riferimento per lo sviluppo. Non è una specifica funzionale né un elenco di feature: è una raccolta di **casistiche, ambiguità e trappole** da tenere presenti durante la progettazione del data model, della logica applicativa e della UI. Ogni sezione descrive un'area problematica e le domande a cui il design deve rispondere prima di scrivere codice.

**Specifica derivata:** [data-model-specification.md](data-model-specification.md) — traduce queste considerazioni in entità, persistenza, undo, impostazioni e import (EPLAN, ecc.).

**Guida progettista:** [guida-progettazione-schema-elettrico.md](guida-progettazione-schema-elettrico.md) — norme, best practice, checklist e tutorial schema (prospettiva operatore, non software).

---

## 1. Identità e rappresentazione multipla dei componenti

Un componente fisico (es. un contattore KM1) esiste simultaneamente in tre "mondi" distinti, ognuno con la propria rappresentazione:

- **Mondo schematico**: simbolo elettrico funzionale — bobina su un foglio, contatti di potenza su un altro, ausiliari su altri ancora
- **Mondo layout quadro**: sagoma fisica 2D sulla guida DIN, con ingombro reale in mm
- **Mondo dati/BOM**: record in distinta materiali con codice articolo, costruttore, quantità, prezzo

Il data model deve rispondere a:

- Come si mantiene la coerenza tra le tre rappresentazioni quando si modifica una property (es. si cambia la taglia del contattore)?
- Chi è il "master"? Se cambio il componente nel layout, si aggiorna lo schema? E viceversa?
- Come si gestisce un componente presente nello schema ma non ancora posizionato nel layout (fase di progettazione anticipata)?
- Come si gestisce un componente presente nel layout ma non ancora cablato nello schema?

---

## 2. Decomposizione fisica dei componenti — figli, sottocomponenti e parti

Un singolo componente commerciale (un contattore, un pulsante, un connettore) è fisicamente composto da parti che hanno vita propria nel disegno elettrico.

### Contattore (es. Schneider LC1D09)

- Corpo principale con contatti di potenza (3NA o 4NA)
- Bobina (con tensione nominale — parametro fondamentale)
- Blocchi ausiliari montabili lateralmente (NA, NC, in quantità configurabile)
- Blocco di soppressione della bobina (RC, diodo, varistori — parametro)
- Contatti speciali (contatto a specchio, contatto anticipato)

Il numero e il tipo di contatti ausiliari **dipende dalla configurazione hardware**: non è fisso nella definizione del componente. Il CAD deve sapere quanti slot ausiliari ha il corpo, quali blocchi sono stati montati, e di conseguenza quanti contatti sono disponibili per il collegamento.

### Pulsante (es. Schneider XB4)

- **Testa** (parte frontale): pulsante, selettore, chiave, fungo d'emergenza — determina il simbolo grafico
- **Housing/corpo** (parte sul pannello): colore, diametro, profilo di montaggio
- **Blocchi contatto** (parte posteriore): NA, NC, montabili in sequenza, con numero variabile
- **LED/spia** integrata: alimentazione, colore

Un pulsante XB4 può avere 0, 1, 2 o più blocchi contatto sovrapposti. La stessa testa può montare blocchi diversi. Il codice articolo del componente fisico **non è uno solo**: è la combinazione di testa + blocchi + eventuale LED. Il CAD deve:

- Gestire il componente come aggregazione di sottoparti
- Mostrare nello schema tutti i contatti montati (anche se distribuiti su fogli diversi)
- Generare la BOM correttamente: non "1x pulsante XB4" ma "1x testa XB4BA31 + 1x blocco ZB4BZ101 + 1x blocco ZB4BZ102"
- Validare che i blocchi scelti siano compatibili con quella testa

### Implicazione per il data model

La struttura non è piatta. Un `ComponentInstance` può avere:

- `subcomponents`: lista di sottoparti fisiche (blocchi, moduli, accessori)
- `fragments`: lista di apparizioni grafiche sugli schemi (bobina, contatti, corpo pulsante)

Le due liste sono ortogonali: un sottocomponente (blocco ausiliario fisico) può generare uno o più fragment grafici in punti diversi dello schema.

---

## 3. Connettori — la complessità nascosta

Un connettore sembra semplice ma nasconde molte casistiche:

### Accoppiamento maschio/femmina

- Ogni connettore ha una controparte fisica (plug + socket). Il CAD deve sapere che XP1 (maschio su cavo) si accoppia con XS1 (femmina su quadro).
- I pin devono essere numerati in modo speculare (pin 1 di XP1 → pin 1 di XS1) o con mapping custom.
- L'ERC deve verificare che maschio e femmina abbiano lo stesso numero di pin e che i segnali assegnati siano compatibili.

### Pin non collegati vs pin assenti

- Un connettore M12 a 8 pin può avere solo 5 pin cablati: i restanti 3 sono fisicamente presenti ma non usati. Non è un errore ERC, ma va documentato.
- Alcuni connettori hanno pin meccanici (guida, blocco) senza funzione elettrica: non devono apparire nella netlist.

### Connettori multipolari con schermatura

- Lo schermo del cavo può essere collegato al connettore tramite il corpo (connessione a 360°) o tramite un pin dedicato (drain wire).
- Il collegamento dello schermo segue regole diverse dai pin normali: tipicamente collegato solo a un'estremità.

### Connettori composti (es. HAN, MIXO)

- Un connettore industriale HAN può contenere più inserti: insert di potenza + insert segnali + insert pneumatico nello stesso corpo.
- Ogni inserto è un componente separato con i propri pin, ma tutti condividono lo stesso corpo fisico e la stessa numerazione meccanica.

### Connettori su più fogli

- Un connettore di campo (es. morsettiera su un motore) appare nello schema elettrico, nel layout quadro, e nella documentazione di cablaggio. Le tre rappresentazioni devono essere sincronizzate.

---

## 4. Cavi — unipolari, multipolari, schermati, speciali

### Il filo unipolare

Il caso più semplice: un singolo conduttore da punto A a punto B. Ma anche qui:

- Ha un colore (normato IEC 60757: BK, BU, GNYE, RD, OG, WH...)
- Ha una sezione (mm²) che deve essere compatibile con la corrente del circuito
- Ha una tensione nominale (450/750V, 300/500V...)
- Può essere flessibile o rigido
- Ha un nome/numerazione che compare sull'etichetta

### Il cavo multipolare

Un cavo multipolare è un'entità di primo livello, non solo un gruppo di fili:

- Ha un codice articolo proprio (es. FG16OR16 3x2.5mm²)
- Contiene anime (cores) con colori e sezioni proprie
- Ogni anima è indipendentemente collegabile a net diverse
- Ha un percorso fisico (canaline, passacavi, tubi) che determina la lunghezza
- Ha un riferimento (W1, W2...) che compare sulle etichette delle anime
- Può avere schermatura con le sue regole di collegamento

Domanda chiave per il data model: il filo unipolare è un caso degenere di cavo multipolare (cavo con una sola anima) oppure è un tipo fondamentalmente diverso? La risposta impatta tutta la gestione dei cavi.

### Cavi speciali

- **Bus di campo**: Profibus (viola), CANopen, DeviceNet — colori e struttura definiti dalla norma, impedenza controllata, non intercambiabili con cavi generici
- **Cavi di segnale schermati**: termocoppie, PT100, encoder — la schermatura è parte del segnale, non solo protezione EMC
- **Cavi di sicurezza**: SIL/PLd — devono essere tracciati separatamente, non mischiati con altri cavi nello stesso tubo
- **Fibra ottica**: nessuna proprietà elettrica ma presente nel layout e nella documentazione

### Lunghezza cavi

La lunghezza è un dato ambiguo:

- Può essere stimata (dalla posizione nel layout quadro 2D + percorso ipotetico)
- Può essere misurata (dato reale dopo installazione)
- Può essere fornita dal cliente (per cavi di campo)
- Può essere calcolata con tolleranza (lunghezza geometrica + extra per allacciamenti + margine)

Il CAD deve gestire questi stati distinti, non collassarli in un singolo campo numerico.

---

## 5. Morsettiere — ben più di una lista di morsetti

### Tipi di morsetto

Un morsetto non è solo "un posto dove attaccare un filo". I tipi principali:

- **Passante standard**: collegamento diretto tra filo superiore e inferiore
- **Passante doppio/triplo/quadruplo**: più livelli di connessione indipendenti nello stesso corpo fisico (es. Phoenix PT 4/2 — due circuiti separati nello stesso alloggio)
- **Con fusibile**: il circuito passa attraverso un fusibile estraibile — il morsetto ha uno stato (fusibile presente/assente, fuso/integro)
- **Con sezionatore**: possibilità di aprire il circuito senza disconnettere i fili
- **Con diodo**: per circuiti DC con protezione da inversione
- **PE/terra**: connesso obbligatoriamente alla guida DIN metallica (non è un semplice passante)
- **Neutro (N)**: simile al PE ma con regole normative diverse
- **Schermo/shield**: con connessione capacitiva alla terra, senza connessione galvanica diretta

### Ponticelli (bridges/jumpers)

I ponticelli collegano elettricamente morsetti adiacenti senza fili visibili nello schema:

- Possono collegare 2, 3, 4 o N morsetti consecutivi
- Hanno un lato (superiore o inferiore, o entrambi)
- Cambiano la topologia elettrica senza apparire come fili nello schema: sono un'eccezione alla regola "ogni connessione è una net esplicita"
- Devono essere documentati nel disegno della morsettiera
- L'ERC deve saperli attraversare quando calcola la continuità

### La morsettiera come entità

Una morsettiera (es. X1) non è solo una lista di morsetti:

- Ha un ordinamento fisico (da sinistra a destra)
- Può contenere separatori (meccanici, per suddividere gruppi funzionali)
- Può avere segna-morsetti (etichette di gruppo)
- Ha un punto di inizio sulla guida DIN
- I numeri dei morsetti non sono necessariamente sequenziali (possono esserci salti, riserve)
- Può essere divisa su più fogli dello schema ma rimane un'unica entità fisica

### Morsetti con figli

Un morsetto doppio (es. due livelli) nello schema elettrico appare come DUE simboli separati (uno per ogni livello), ma è UN solo componente nella BOM e UN solo oggetto nel layout quadro. Stessa trappola del contattore: la molteplicità schematica vs l'unicità fisica.

---

## 6. PLC e dispositivi con configurazione hardware variabile

Un PLC è il caso estremo di componente i cui pin dipendono dalla configurazione:

### Il problema dei pin dinamici

A differenza di un contattore (dove i pin sono fissi una volta scelti i blocchi), un PLC S7-1200 con rack espandibile può avere configurazioni radicalmente diverse:

- CPU1214C standalone: 14DI + 10DO + 2AI integrati
- Stessa CPU + 2×SM1221 (16DI ciascuno): totale 46DI + 10DO + 2AI
- Configurazione completamente diversa con SM analogici: pin totalmente differenti

Il numero di I/O fisici (e quindi di pin disponibili nello schema) non si conosce finché non si definisce la configurazione hardware. Il CAD deve:

- Permettere di definire la configurazione hardware (rack, slot, moduli)
- Generare dinamicamente i pin dell'istanza PLC in base a questa configurazione
- Validare che i moduli scelti siano compatibili con quella CPU (es. limite di espansione)
- Permettere di collegare i pin I/O alle net dello schema

### Indirizzi I/O

Ogni pin I/O ha un indirizzo logico (I0.0, Q1.3, IW64...) oltre al nome fisico. Questo indirizzo:

- Dipende dalla posizione del modulo nel rack
- Può essere riassegnato dall'utente
- Deve essere coerente con la configurazione nel software PLC (TIA Portal, Studio 5000...)
- Deve apparire nella lista segnali I/O (fondamentale per il collaudo)

La lista I/O è uno dei documenti più usati sul campo: deve essere generabile dal CAD in formato compatibile con lo strumento di programmazione PLC.

### Bus di campo e dispositivi remoti

Un ET200SP, un nodo DeviceNet, un drive con scheda bus non sono PLC ma seguono la stessa logica: configurazione hardware variabile, indirizzi logici, connessione al master tramite cavo bus (non cavi individuali per ogni segnale).

---

## 7. Il simbolo schematico vs il codice articolo vs il simbolo di layout

Questa è una delle distinzioni più sottili e più importanti:

### Tre entità distinte

**Il simbolo schematico** rappresenta la funzione elettrica. Un interruttore magnetotermico monofase è sempre disegnato allo stesso modo (IEC 60617), indipendentemente dal costruttore.

**Il codice articolo** è il prodotto commerciale specifico: Schneider iC60N 1P 16A curva C. Ha dimensioni fisiche, peso, datasheet, prezzo, disponibilità.

**Il simbolo di layout** è la sagoma 2D nel layout quadro: larghezza in moduli DIN, altezza in mm, posizione dei morsetti, punto di ancoraggio.

### La trappola della confusione

Molti CAD (e molti progettisti) trattano queste tre cose come una sola. Le conseguenze:

- Se leghi il simbolo schematico al codice articolo, non puoi cambiare il costruttore senza modificare lo schema
- Se leghi il codice articolo al simbolo di layout, non puoi fare una variante con diverso costruttore nel layout senza duplicare tutto
- Se non hai il simbolo di layout separato, non puoi fare layout quadro automatico

Il design corretto mantiene le tre entità separate con relazioni esplicite:

```
SymbolDefinition (funzione elettrica, norma IEC)
    ↓ "può essere rappresentato da"
ComponentDefinition (caratteristiche tecniche, categoria)
    ↓ "ha come prodotto commerciale"
PartNumber (codice articolo, costruttore, dati commerciali)
    ↓ "ha come ingombro fisico"
FootprintDefinition (sagoma 2D per layout quadro)
```

In fase di progettazione preliminare puoi avere `ComponentDefinition` senza `PartNumber` (non hai ancora scelto il costruttore). In fase di acquisto assegni il `PartNumber`. In fase di layout assegni il `FootprintDefinition`.

### Grafica componibile e allegati (estensione al modello)

Oltre alle tre entità «funzione / prodotto / ingombro», conviene separare anche la **grafica schematica** dalla semantica IEC:

- **Celle base riusabili** (`GraphicCellDefinition`) — un contatto NA, una bobina, un arco: elementi standard da catalogo.
- **Composizione** (`SymbolGraphicComposition`) — es. interruttore 3 poli = **3×** la stessa cella contatto + eventuali celle aggiuntive (maniglia, arco di separazione).
- **Simbolo funzionale** (`SymbolDefinition`) — punta alla composizione e definisce i pin logici; la grafica può cambiare senza cambiare la funzione elettrica.

Questo rende la grafica **declarativa e generabile da AI**: l'assistente compone da celle già in libreria (validazione Pydantic), invece di disegnare SVG arbitrario.

Ogni livello catalogo e ogni `Device` di progetto possono avere **immagini e documenti** (`MediaAttachment`: datasheet PDF, foto prodotto, anteprima cella grafica). Dettaglio in [data-model-specification.md §5.1–§5.2](data-model-specification.md).

---

## 8. Numerazione — più complessa di quanto sembri

### Referenze componenti

La referenza (KM1, F3, Q2...) sembra banale ma ha molte varianti:

- Per tipo globale al progetto: KM1, KM2, KM3... tutti i contattori del progetto
- Per tipo per funzione/macchina: ogni sottosistema riparte da 1
- Per foglio: ogni foglio ha la propria numerazione
- Con prefisso funzionale: +QUADRO1-KM1 (notazione IEC 81346)

### IEC 81346 — identificazione strutturata

La norma IEC 81346 definisce un sistema di identificazione gerarchico:

- `=` prefix: sistema/funzione (es. `=CONVEYOR`)
- `+` prefix: locazione (es. `+PANEL_A`)
- `-` prefix: componente (es. `-KM1`)

Una referenza completa è `=CONVEYOR+PANEL_A-KM1`. Il CAD deve supportare questo sistema o almeno non impedirlo. Questo impatta direttamente il data model dei componenti e la generazione di tutti i report.

### Numerazione fili

Un filo può essere numerato:

- Per potenziale (tutti i fili del potenziale "24VDC+" hanno lo stesso numero)
- Sequenzialmente per foglio (ogni collegamento ha un numero progressivo)
- Con il numero del morsetto di destinazione (usato in Germania, norma DIN)
- Combinazione di criteri

Ogni schema di numerazione produce etichette diverse. Il CAD deve supportare regole configurabili per progetto, non hard-coded.

---

## 9. Potenziali, net e propagazione — la logica elettrica sottostante

### Net vs Potenziale

Sono concetti diversi che spesso vengono confusi:

**Net** (rete): insieme di conduttori fisicamente connessi — è un concetto topologico/grafico.

**Potenziale**: valore elettrico di una net — è un concetto fisico/elettrico. Due net separate da un contatto aperto hanno la stessa net? No. Ma potrebbero avere lo stesso potenziale quando il contatto è chiuso.

Il CAD schematico lavora con net (cosa è connesso a cosa nel disegno). L'analisi elettrica lavora con potenziali (cosa vale cosa in esercizio). La confusione tra i due porta a ERC scorretti.

### Propagazione attraverso elementi

Alcune connessioni sono conduttive per definizione (fili, morsetti). Altre dipendono dallo stato:

- Contatto NA aperto: non propaga (di default)
- Contatto NA chiuso: propaga
- Morsetto con fusibile fuso: non propaga
- Ponticello: propaga sempre

Per l'ERC statico (senza simulazione) il CAD tipicamente considera solo le connessioni fisiche (ignora gli stati). Ma per la verifica del potenziale PE, per esempio, deve propagare attraverso la continuità di messa a terra anche attraverso morsetti PE e guida DIN.

### Net globali

Alcune net sono globali (presenti su tutti i fogli senza bisogno di simboli di continuità):

- PE (terra di protezione)
- N (neutro)
- Potenziali di alimentazione standard (es. "24VDC+", "0VDC")

Altre net sono locali a un foglio o a un sottosistema. Il CAD deve permettere di definire quali net sono globali e quali no.

---

## 10. Revisioni — non è solo un numero di versione

### Cosa cambia tra revisioni

Una revisione documentale di un progetto è formalmente diversa da una modifica tecnica:

- **Revisione grafica** (A, B, C...): cambia il contenuto tecnico. Ogni foglio modificato incrementa la propria revisione.
- **Emissione** (00, 01, 02...): rilascio formale del progetto al cliente o alla produzione. Congela lo stato di tutti i fogli.

Il CAD deve gestire entrambi i livelli indipendentemente.

### Revision cloud

Nel disegno tecnico, le modifiche tra revisioni vengono evidenziate graficamente con una "nuvola" di revisione: un'area tratteggiata che circoscrive la parte modificata. È un requisito normativo in molti settori industriali. Il CAD deve permettere di disegnare queste nuvole e associarle a una revisione specifica.

### Blocco delle revisioni approvate

Un foglio in stato "approvato" o "emesso" non può essere modificato senza:

1. Alzare la revisione del foglio
2. Eventualmente alzare l'emissione del progetto

Il CAD deve implementare questo workflow e non permettere modifiche "silenziose" su fogli già approvati.

---

## 11. Persistenza — più livelli con requisiti diversi

### File di progetto

Il file di progetto deve essere:

- **Apribile offline**: non dipende da un server
- **Versionabile con Git**: testo (JSON) non binario
- **Diffabile**: si deve poter vedere cosa è cambiato tra due versioni
- **Robusto alla corruzione parziale**: se un foglio è corrotto, gli altri devono essere ancora apribili

Implicazione: un progetto non è un singolo file monolitico ma una cartella con file separati per ogni foglio/risorsa, compressa in un archivio con formato documentato.

### Libreria componenti

Requisiti diversi dal progetto:

- **Ricercabile rapidamente** per nome, categoria, costruttore, codice articolo
- **Condivisa** tra più utenti/progetti
- **Aggiornabile** indipendentemente dai progetti che la usano
- **Con storico**: se cambia la definizione di un componente, i progetti precedenti non devono rompersi

SQLite è appropriato. Ma serve un meccanismo di "versioning" delle definizioni: ogni `ComponentDefinition` ha una versione, e le istanze nei progetti referenziano una versione specifica, non l'ultima.

### Autosave e recovery

L'autosave non è solo "salva ogni N minuti". Deve gestire:

- Il file di recovery è separato dal file di progetto (non sovrascrivere un file salvato manualmente con un autosave)
- Al riavvio dell'applicazione, se esiste un recovery più recente del file su disco, chiedere all'utente cosa fare
- I recovery vecchi di X giorni vengono eliminati automaticamente
- L'autosave non blocca l'UI (scrittura asincrona)

### Undo/Redo

Lo stack di undo non è persistito su disco (si perde alla chiusura). Ma:

- Deve avere un limite configurabile (memoria vs profondità)
- Le operazioni "pesanti" (elimina 50 componenti) devono essere un singolo passo di undo
- Alcune operazioni non sono undoable (es. rinominare un file, cambiare impostazioni applicazione)
- Il merge di undo con autosave è delicato: salvare il file non dovrebbe svuotare lo stack di undo

---

## 12. Impostazioni — tre livelli che si sovrappongono

### Livello applicazione

Preferenze dell'installazione locale:

- Percorsi librerie, percorso progetti default
- Lingua UI
- Tema (chiaro/scuro)
- Shortcut tastiera
- Comportamento autosave (intervallo, numero di recovery mantenuti)

### Livello progetto

Regole specifiche del progetto, scritte nel file di progetto:

- Norma di riferimento (IEC, NFPA, GB...)
- Schema di numerazione componenti e fili
- Prefissi e suffissi per le referenze
- Formato fogli default, cartiglio
- Net globali del progetto
- Lingua del progetto (per export documenti)

### Livello utente

Preferenze dell'utente che lavorano sopra le impostazioni applicazione:

- Layout dei pannelli UI
- Zoom e posizione su ogni foglio (dove ero la volta scorsa che ho aperto questo foglio)
- Elementi recenti, preferiti

### Conflitti tra livelli

Il livello progetto sovrascrive il livello applicazione per le impostazioni rilevanti al progetto. Un progetto impostato su norma NFPA deve rimanere NFPA anche se l'installazione locale è configurata IEC. Questo deve essere esplicito e documentato nel data model.

---

## 13. Template e macro — riuso strutturato

### Macro vs Template — distinzione critica

**Template** (modello): punto di partenza per un nuovo elemento. Viene copiato e diventa indipendente dall'originale. Modificare il template non modifica le istanze esistenti.

**Macro** (con link al master): istanza collegata a una definizione master. Modificare il master propaga la modifica a tutte le istanze. Come i "blocchi" in AutoCAD o i "componenti" in Figma.

Il CAD deve supportare entrambi i concetti. Confonderli porta a uno dei due errori comuni:
- Usare solo template: impossibile aggiornare in massa un circuito standard usato in 30 progetti
- Usare solo macro: modificare una macro per un progetto specifico rompe tutti gli altri

### Parametrizzazione delle macro

Una macro "avviatore diretto" non è utile se ha la corrente nominale hard-coded. Deve avere parametri:

- Corrente nominale motore → dimensiona l'interruttore e il relè termico
- Tensione bobina → sceglie la bobina del contattore giusta
- Numero di rifasamento → aggiunge o rimuove il blocco condensatori

La parametrizzazione può essere semplice (l'utente inserisce i valori al momento dell'inserimento) o intelligente (il CAD propone valori standard in base ai parametri inseriti).

---

## 14. Multi-lingua e localizzazione

Non è solo tradurre la UI. In un CAD elettrico la lingua è un dato di progetto:

- Le descrizioni dei componenti possono essere multilingua (IT + EN + DE)
- Le etichette sui disegni (cartiglio, note) devono essere generabili in lingua cliente
- I simboli hanno nomi diversi in IEC vs NFPA (es. il simbolo del motore)
- I formati numerici (virgola decimale vs punto) impattano la lettura di file di configurazione

Implicazione: ogni stringa di testo visibile nel progetto (non nella UI) dovrebbe essere potenzialmente traducibile. Questo è un requisito architetturale, non può essere aggiunto dopo.

---

## 15. Performance con progetti grandi

Un progetto reale di un quadro industriale medio può contenere:

- 50-200 fogli schematici
- 500-2000 componenti
- 2000-8000 net
- 100-500 cavi

Un progetto grande (impianto completo):

- 500-2000 fogli
- 5000-20000 componenti

Le implicazioni architetturali sono significative:

- **Non caricare tutto in memoria**: i fogli non attivi devono rimanere su disco, caricati on-demand
- **Indici per ricerca rapida**: trovare tutti i contatti di KM1 su 500 fogli deve essere istantaneo
- **Rendering differenziale**: ridisegnare solo la parte di scheda modificata, non tutta la scene
- **ERC incrementale**: non ricalcolare l'intero ERC ad ogni modifica, ma solo la parte impattata
- **Report in background**: generare un PDF di 200 pagine non deve bloccare l'UI

Questi sono requisiti che impattano il data model fin dall'inizio. Un modello che carica tutto in un dizionario Python in memoria funziona benissimo fino a 50 fogli e diventa inutilizzabile a 500.

---

## 16. Integrazione AI — considerazioni specifiche per il dominio elettrico

L'AI che lavora su questo dominio ha caratteristiche particolari rispetto all'AI generica:

### L'output deve essere sempre validabile

L'AI genera un `ComponentGroup` (es. un avviatore stelle-triangolo). Prima di inserirlo nel progetto, il CAD deve eseguire:

- Validazione del JSON rispetto ai modelli Pydantic
- Verifica che tutti i `ComponentDefinition` referenziati esistano nella libreria
- ERC preliminare del gruppo (le net interne sono coerenti?)
- Verifica che i parametri rispettino i vincoli (es. corrente > 0, tensione in valori standard)

Non si inserisce mai output AI direttamente senza validazione.

### Il contesto che l'AI riceve è determinante

Per generare qualcosa di utile, l'AI deve sapere:

- Quali componenti sono già nel progetto (per evitare conflitti di referenza)
- Quali net esistono già (per collegarsi correttamente)
- Quali sono i parametri del sistema (tensione di alimentazione, corrente disponibile)
- Quali sono le convenzioni del progetto (prefissi, norme)

Il CAD deve costruire e passare questo contesto in modo strutturato, non fare prompt generici.

### L'AI come assistente, non come autore

L'utente rimane responsabile del progetto. L'AI propone, l'utente approva. Il workflow deve essere:

1. L'utente descrive cosa vuole
2. L'AI genera una proposta (visibile, non ancora nel progetto)
3. L'utente rivede e modifica la proposta
4. L'utente approva l'inserimento
5. Il CAD esegue la validazione e inserisce

Non esiste un "fai tutto automaticamente senza mostrarmelo".

---

## 17. Export e interoperabilità — non è solo PDF

### Export per la produzione

Il documento più importante non è il PDF per il cliente ma il **documento di cablaggio per il cablatore**:

- Lista fili ordinata per morsettiera di partenza
- Lista fili ordinata per morsettiera di arrivo
- Lista fili ordinata per cavo (tutte le anime di W1, poi W2...)
- Lunghezze cavi con tolleranza

Questi documenti devono essere personalizzabili: ogni azienda ha il suo formato, il suo cablatore ha le sue abitudini.

### Export per etichettatura

Le stampanti di etichette (Brady BMP71, HellermannTyton TAG, Partex) hanno formati proprietari. L'export deve generare file che la stampante può leggere direttamente, non PDF da cui il cablatore riscrive tutto a mano.

### Import da costruttori

I costruttori (Schneider, ABB, Siemens, Phoenix Contact) forniscono dati dei componenti in formati diversi: ECLASS XML, ETIM, Excel custom. Il CAD deve poter importare questi dati nella libreria locale senza richiedere inserimento manuale.

### Compatibilità con altri CAD

Progetti reali spesso provengono da o devono andare verso altri CAD (EPLAN, AutoCAD Electrical, SEE Electrical). Non esiste uno standard universale per gli schemi elettrici (a differenza di STEP/IFC per il meccanico). L'unica via pratica è DXF (geometria senza dati) per la compatibilità minima, o formati proprietari per la compatibilità completa.

---

## Note finali per il progettista

Queste considerazioni non sono tutte da implementare subito. Alcune (multi-lingua, integrazione ERP, revisioni formali) possono aspettare. Altre (separazione simbolo/componente/footprint, componenti con sottoparti, net globali, performance con progetti grandi) devono essere nel data model fin dal giorno 1 perché aggiungerle dopo richiede una riscrittura.

La regola pratica: tutto ciò che impatta la struttura dei dati va deciso prima. Tutto ciò che impatta solo la UI o i report può essere aggiunto incrementalmente.

---

## Documenti correlati

- [data-model-specification.md](data-model-specification.md) — specifica data model (dominio, persistenza, undo, settings, import)
- [import-eplan-mapping-notes.md](import-eplan-mapping-notes.md) — mapping import EPLAN
- [data-model-open-questions.md](data-model-open-questions.md) — decisioni aperte
- [README.md](README.md) — indice cartella `docs/idea/`
