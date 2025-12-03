# Development Guide

## Quick Setup

```bash
# Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate schemas and example files
python3 scripts/build_schemas.py

# Validate
python3 scripts/validate_schemas.py
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

3. Regenerate: `python3 scripts/build_schemas.py`
4. Test: `python3 scripts/validate_schemas.py`

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

## Generated Schemas

**Core:**

- `dispositif-aide.json`

**Usage only:**

- `dispositif-aide-{communication,pilotage,activation}.json`

**Target only:**

- `dispositif-aide-{associations,particuliers,...}.json`

**Combined:**

- `dispositif-aide-{target}-{usage}.json`
- `dispositif-aide-{target}-{usage1}-{usage2}.json`

Each target is independent of the others.
Multiple usages can be combined with each target.

## Supported Field Types

- `string` - Text (default)
- `integer` - Whole number
- `number` - Decimal number
- `boolean` - true/false
- `date` - YYYY-MM-DD
- `datetime` - ISO 8601
- `array`, `object`, `year`, `yearmonth`, `duration`, `geopoint`, `geojson`

See [Frictionless specs](https://specs.frictionlessdata.io/table-schema/) for details.

## Workflow

1. Modify source files in the schema directory (core or extensions)
2. Regenerate: `python3 scripts/build_schemas.py`
3. Validate: `python3 scripts/validate_schemas.py`
4. Commit everything (source + generated schemas)

## References

- [Frictionless Data Specs](https://specs.frictionlessdata.io/)
- [Table Schema Spec](https://specs.frictionlessdata.io/table-schema/)
- [Data Package Spec](https://specs.frictionlessdata.io/data-package/)
