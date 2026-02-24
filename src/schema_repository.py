"""Repository for schema persistence (read/write operations)."""

import json
from pathlib import Path
from typing import Dict, Tuple


class SchemaRepository:
    """Handles loading and saving of schema and extension files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.schema_dir = repo_root / "schema"
        self.core_path = self.schema_dir / "core" / "schema-core.json"
        self.extensions_dir = self.schema_dir / "extensions"
        self.usage_dir = "usage"
        self.cible_dir = "cible"

    def load_schema(self, path: Path) -> Dict:
        """Load a JSON schema file."""
        if not path.exists():
            raise FileNotFoundError(f"Schema not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_schema(self, schema: Dict, path: Path) -> None:
        """Save a schema to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

    def load_core_schema(self) -> Dict:
        """Load the core schema."""
        return self.load_schema(self.core_path)

    def load_extensions(self) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
        """
        Load all extensions.

        Returns:
            Tuple of (usage_extensions, cible_extensions)
        """
        usage_extensions = {}
        cible_extensions = {}

        usage_dir = self.extensions_dir / self.usage_dir
        if usage_dir.exists():
            for extension_file in sorted(usage_dir.glob("*.json")):
                extension_data = self.load_schema(extension_file)
                usage_extensions[extension_data["name"]] = extension_data

        cible_dir = self.extensions_dir / self.cible_dir
        if cible_dir.exists():
            for extension_file in sorted(cible_dir.glob("*.json")):
                extension_data = self.load_schema(extension_file)
                cible_extensions[extension_data["name"]] = extension_data

        return usage_extensions, cible_extensions
