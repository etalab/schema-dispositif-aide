# Guide d'utilisation

## Workflow automatisé

**GitHub Actions génère et valide automatiquement les schémas** lorsque sont détextées des modifications dans `schema/` lors d'un push. 

Vous n'avez qu'à modifier les fichiers sources dans `schema/core/` et `schema/extensions/` et commit le tout dans une branche puis la push sur github.

## Modifier un schéma

1. Ouvrir le fichier JSON concerné (core ou extension), ex: `schema/extensions/{category}/{name}.json`
Catégory étant limité à "cible" ou "usage".
(Autoriser plus d'option, nécessiterait d'introduire plus d'éléments de configuration, notamment pour pouvoir automatiquement savoir quelles combinaisons générer entre les différents catégories et les différents éléments de chaque catégorie.)

2. Ajouter un champ dans le tableau `fields` :

```json
{
  "name": "nom_du_champ",
  "title": "Titre du champ",
  "description": "Description",
  "type": "string",
  "example": "valeur d'exemple",
  "constraints": {
    "required": true,
    "maxLength": 500
  }
}
```

3. Commit et push - GitHub Actions régénère et valide automatiquement les schémas

## Ajouter une extension (cible ou usage)

Le repo génère automatiquement toutes les combinaisons d'usages pour chaque cible.

Pour ajouter une nouvelle cible ou un nouvel usage :
1. Créer un fichier JSON dans `schema/extensions/cible/` ou `schema/extensions/usage/`
2. Suivre le format des fichiers existants
3. Commit et push - les schémas combinés sont générés automatiquement 

# Development Guide

## Quick Setup

```bash
# Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate schemas and example files (optional - automated via GitHub Actions)
python3 src/build_schemas.py

# Validate (optional - automated via GitHub Actions)
python3 src/validate_schemas.py
```

## Architecture

The repo uses a modular datapackage structure:

- **Core schema** (`schema/core/schema-core.json`) - Base fields required for all schemas
- **Extensions** - Optional fields for specific use cases (usage & target audience)
- **Build script** - Generates schemas for all combinations of usage for each target

```
schema/
├── core/schema-core.json
└── extensions/
    ├── usage/
    │   ├── communication.json
    │   ├── pilotage.json
    │   └── activation.json
    └── cible/
        ├── associations.json
        ├── particuliers.json
        ├── professionnels.json
        └── secteur-public.json
```

## Common Tasks

### Add a Field

1. Open the relevant JSON file (core or extension), ex: `schema/extensions/{category}/{name}.json`
2. Add to the `fields` array:

```json
{
  "name": "field_name",
  "title": "Field Title",
  "description": "Description",
  "type": "string",
  "example": "example value"
}
```

3. Commit and push - GitHub Actions will automatically regenerate and validate schemas
4. (Optional) Test locally: `python3 src/build_schemas.py && python3 src/validate_schemas.py`

### Create an Extension

The simplest way is to copy an existing extension for reference.

The written code automatically handles new targets or usages but needs to be edited if a new category of extensions is created.

Currently, there is no generic logic to handle a new type of extension.
In particular, the associations between extensions in this new category should be defined, and the allowed combinations between extension categories should be defined.

### Resolve Field Conflicts

When fields with the same name have different types, you'll get warnings. Resolve by:

**Option 1: Rename** - Use different names in different extensions

```json
// In usage/pilotage.json
{"name": "budget_total_alloue", "type": "number"}

// In cible/individuals.json
{"name": "budget_per_person", "type": "string"}
```

**Option 2: Harmonize** - Use the same type everywhere

```json
{ "name": "budget", "type": "number" }
```

**Future enhancements:**
Handle priority fields to allow overriding some fields. (Identified use case: make a field mandatory within an extension).

## Testing

```bash
# Validate a specific schema
frictionless validate build/schemas/dispositif-aide-pilotage.json

# Validate data against a schema
frictionless validate data.csv --schema build/schemas/dispositif-aide.json

# Validate all schemas
python3 scripts/validate_schemas.py
```

When working on the code, the evolutions should be tested with 
```bash
python -m unittest tests/test_*.py
```
## References

- [Frictionless Data Specs](https://specs.frictionlessdata.io/)
- [Table Schema Spec](https://specs.frictionlessdata.io/table-schema/)
- [Data Package Spec](https://specs.frictionlessdata.io/data-package/)
