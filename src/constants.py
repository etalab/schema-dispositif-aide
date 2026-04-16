"""Project-wide path constants and naming conventions."""

from pathlib import Path

# --- source schemas (relative to repo root) ---
SCHEMA_DIR = Path("schema")
SCHEMA_CORE = SCHEMA_DIR / "core" / "schema-core.json"
SCHEMA_EXTENSIONS = SCHEMA_DIR / "extensions"

# --- build outputs (relative to repo root) ---
BUILD_SCHEMAS = Path("build") / "schemas"
BUILD_EXEMPLES = Path("build") / "exemples"
BUILD_EXEMPLES_PAR_SCHEMA = BUILD_EXEMPLES / "par_schema"
DATAPACKAGE = Path("datapackage.json")

# --- schema naming ---
BASE_NAME = "dispositif-aide"
BASE_TITLE = "Dispositifs d'aides"

# --- datapackage metadata ---
DATAPACKAGE_NAME = "schemas-dispositif-aide"
DATAPACKAGE_TITLE = "Schémas des dispositifs d'aide"
DATAPACKAGE_DESC = "Schémas de données permettant de décrire plus ou moins précisément les dispositifs d'aide"

# --- resource metadata ---
RESOURCE_CSV_LABEL = "Fichier de validation (CSV)"
EXEMPLE_COMPLET_CSV = "exemple-complet.csv"
DOCUMENTATION = "README.md"


def csv_filename(name: str) -> str:
    """Canonical CSV example filename."""
    return f"exemple-{name}.csv"


def schema_resource_name(name: str) -> str:
    """Frictionless resource name for a schema's CSV example."""
    return f"{csv_filename(name).removesuffix('.csv')}-csv"


def schema_resource_csv_path(name: str) -> str:
    """CSV path embedded in a schema resource (relative to build/)."""
    rel = BUILD_EXEMPLES_PAR_SCHEMA.relative_to(BUILD_SCHEMAS.parent)
    return (rel / csv_filename(name)).as_posix()


def datapackage_csv_path(name: str) -> str:
    """CSV path embedded in datapackage.json (relative to repo root)."""
    return (BUILD_EXEMPLES_PAR_SCHEMA / csv_filename(name)).as_posix()
