# Schemi JSON

Directory per **JSON Schema** delle entità dominio, generati da **Pydantic v2**.

## Workflow

```python
from tqvibecae.model.project import Project
import json

schema = Project.model_json_schema()
# Salvare snapshot versionato, es. project.schema.json
```

- Generare da `Model.model_json_schema()`, non duplicare a mano
- Committare snapshot quando cambia `schema_version` o campi pubblici
- Allineare a `model_dump(mode="json")` / `model_validate()`

## Uso AI

Gli schema alimentano function calling, MCP tools e validazione lato agent.
