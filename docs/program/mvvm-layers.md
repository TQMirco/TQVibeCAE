# MVVM — Layer e responsabilità

## Model

**Dove:** `src/tqvibecae/model/`

- Dati e regole di dominio
- Validazione e invarianti
- Serializzazione `to_dict` / `from_dict`
- Zero import PySide6

**Test:** pytest + Hypothesis, nessun pytest-qt.

## ViewModel

**Dove:** `src/tqvibecae/viewmodel/`

- Stato osservabile per la View
- Traduce azioni utente in Command
- Ascolta eventi Model e emette Signal Qt
- Non importa widget concreti

**Test:** unit con Model mock; integration limitate.

## View

**Dove:** `src/tqvibecae/view/`

- Widget, layout, `.ui`
- Binding a ViewModel
- Nessuna mutazione diretta del Model

**Test:** smoke pytest-qt; logica in Model/ViewModel.

## Commands

**Dove:** `src/tqvibecae/commands/`

- Mutazioni serializzabili
- Undo/redo
- Entry point comune UI + AI

## Services

**Dove:** `src/tqvibecae/services/`

- I/O file, export, rendering helper
- Adapter AI (`services/ai/`) senza dipendenza da View

## Dipendenze

```
View → ViewModel → Model
ViewModel → Commands, Services, Model
Commands → Model
Model → (nessuna dipendenza verso sopra)
```

## QAbstractItemModel

Solo adapter in ViewModel per liste/tabelle Qt.
Fonte di verità: Model di dominio.
