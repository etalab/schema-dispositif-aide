"""Repository for schema persistence (read/write operations)."""

import json
from pathlib import Path

import constants


class SchemaRepository:
    """Handles loading and saving of schema and extension files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.schema_dir = repo_root / constants.SCHEMA_DIR
        self.core_path = repo_root / constants.SCHEMA_CORE
        self.extensions_dir = repo_root / constants.SCHEMA_EXTENSIONS

    @staticmethod
    def load_schema(path: Path) -> dict:
        """Load a JSON schema file."""
        if not path.exists():
            raise FileNotFoundError(f"Schema not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_schema(schema: dict, path: Path) -> None:
        """Save a schema to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

    def load_core_schema(self) -> dict:
        """Load the core schema."""
        return SchemaRepository.load_schema(self.core_path)

    def load_extensions(self, scope: str) -> dict[str, dict]:
        """
        Load all extensions for a given scope.

        Args:
            scope: Either "usage" or "cible"

        Returns:
            Dict mapping extension names to their data
        """
        extensions = {}
        scope_dir = self.extensions_dir / scope
        if scope_dir.exists():
            for extension_file in sorted(scope_dir.glob("*.json")):
                extension_data = SchemaRepository.load_schema(extension_file)
                extensions[extension_data["name"]] = extension_data
        return extensions
