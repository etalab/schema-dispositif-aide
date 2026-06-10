"""Project-wide path constants and naming conventions."""

from pathlib import Path

# --- source schemas (relative to repo root) ---
SCHEMA_DIR = Path("schema")
SCHEMA_CORE = SCHEMA_DIR / "core" / "schema-core.json"
SCHEMA_EXTENSIONS = SCHEMA_DIR / "extensions"

# --- build outputs (relative to repo root) ---
BUILD_DIR = Path("build")
DATAPACKAGE = Path("datapackage.json")

# --- per-schema filenames (inside build/<name>/) ---
SCHEMA_FILENAME = "schema.json"
EXEMPLE_FILENAME = "exemple.csv"
DOCUMENTATION = "README.md"

# Convenience "all fields" example, kept at the build root (not a schema dir).
EXEMPLE_COMPLET_CSV = "exemple-complet.csv"

# --- schema naming ---
BASE_NAME = "dispositif-aide"
BASE_TITLE = "Dispositifs d'aides"

# --- datapackage metadata ---
DATAPACKAGE_NAME = "schemas-dispositif-aide"
DATAPACKAGE_TITLE = "Schémas des dispositifs d'aide"
DATAPACKAGE_DESC = "Schémas de données permettant de décrire plus ou moins précisément les dispositifs d'aide"

# --- resource metadata ---
RESOURCE_CSV_LABEL = "Fichier de validation (CSV)"


def schema_subdir(name: str) -> Path:
    """Directory holding one schema's artifacts (relative to repo root)."""
    return BUILD_DIR / name


def schema_json_path(name: str) -> Path:
    """Path to a schema's JSON file (relative to repo root)."""
    return schema_subdir(name) / SCHEMA_FILENAME


def exemple_path(name: str) -> Path:
    """Path to a schema's example CSV (relative to repo root)."""
    return schema_subdir(name) / EXEMPLE_FILENAME


def readme_path(name: str) -> Path:
    """Path to a schema's README homepage (relative to repo root)."""
    return schema_subdir(name) / DOCUMENTATION


def schema_resource_name() -> str:
    """Frictionless resource name for a schema's CSV example (e.g. ``exemple-csv``)."""
    return EXEMPLE_FILENAME.replace(".", "-")
