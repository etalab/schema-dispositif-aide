"""Main schema builder orchestrator."""

from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

from src.models import BuildResult
from src.schema_loader import SchemaLoader
from src.schema_merger import SchemaMerger
from src.example_generator import ExampleGenerator


class SchemaBuilder:
    """Orchestrates the schema building process."""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.loader = SchemaLoader(self.repo_root)
        self.merger = SchemaMerger()
        self.example_gen = ExampleGenerator(self.repo_root)
        self.build_dir = self.repo_root / "build" / "schemas"

    def get_usage_combinations(self, usage_extensions: Dict) -> List[tuple]:
        """Generate all combinations of usage extensions (0 or more)."""
        usage_names = list(usage_extensions.keys())
        combos = []

        # Empty combination (no usage)
        combos.append(())

        # Single usage extensions
        for name in usage_names:
            combos.append((name,))

        # Multiple usage extensions (2 or more)
        for r in range(2, len(usage_names) + 1):
            for combo in combinations(usage_names, r):
                combos.append(combo)

        return combos

    def generate_schema_name(
        self,
        usage_names: tuple = None,
        cible_name: str = None,
    ) -> str:
        """Generate a schema name from usage and cible components."""
        parts = ["dispositif-aide"]

        if cible_name:
            parts.append(cible_name)

        if usage_names:
            parts.extend(usage_names)

        return "-".join(parts)

    def to_datapackage(self, table_schema: Dict, schema_name: str = None) -> Dict:
        """Convert a table schema to a Frictionless datapackage."""
        resource = {
            "name": table_schema.get("name", "dispositif-aide"),
            "title": table_schema.get("title", "Dispositifs d'aides"),
            "path": (
                f"exemples/exemple-{schema_name}.csv"
                if schema_name
                else "exemple-complet.csv"
            ),
            "schema": {
                "$schema": "https://specs.frictionlessdata.io/schemas/table-schema.json",
                "fields": table_schema.get("fields", []),
                "missingValues": [""],
            },
        }

        datapackage = {
            "name": table_schema.get("name", "dispositif-aide"),
            "title": table_schema.get("title", "Dispositifs d'aides"),
            "description": table_schema.get("description", ""),
            "created": table_schema.get("created"),
            "lastModified": table_schema.get("lastModified"),
            "version": table_schema.get("version"),
            "countryCode": table_schema.get("countryCode"),
            "homepage": table_schema.get("homepage"),
            "licenses": table_schema.get("licenses", []),
            "contributors": table_schema.get("contributors", []),
            "sources": table_schema.get("sources", []),
            "keywords": table_schema.get("keywords", []),
            "resources": [resource],
        }
        return datapackage

    def build_all_schemas(self) -> BuildResult:
        """Build all schema combinations."""
        print("Loading core schema...")
        core_schema = self.loader.load_core_schema()

        print("Loading extensions...")
        usage_extensions, cible_extensions = self.loader.load_extensions()

        print(
            f"Found {len(usage_extensions)} usage extensions: {list(usage_extensions.keys())}"
        )
        print(
            f"Found {len(cible_extensions)} cible extensions: {list(cible_extensions.keys())}"
        )

        # Get all usage combinations
        usage_combos = self.get_usage_combinations(usage_extensions)
        print(f"Will generate {len(usage_combos)} usage combinations")

        # Clean build directory
        self.build_dir.mkdir(parents=True, exist_ok=True)
        for json_file in self.build_dir.glob("*.json"):
            json_file.unlink()

        print("\nGenerating schemas...")

        generated_count = 0
        conflicts = []
        warnings = []
        schemas_for_csv = []
        generated_schemas = {}  # Store schemas for example generation

        # 1. Core only
        core_schema_copy = core_schema.copy()
        core_name = self.generate_schema_name()
        datapackage = self.to_datapackage(core_schema_copy, schema_name=core_name)
        self.loader.save_schema(datapackage, self.build_dir / f"{core_name}.json")
        print(f"✓ {core_name}.json")
        generated_count += 1

        # Get field names for CSV and store schema
        core_field_names = [
            field["name"] for field in core_schema_copy.get("fields", [])
        ]
        schemas_for_csv.append((core_name, core_field_names))
        generated_schemas[core_name] = core_schema_copy

        # 2. Core + usage combinations only (no cible)
        for usage_combo in usage_combos:
            if not usage_combo:
                continue

            usage_exts = [usage_extensions[name] for name in usage_combo]
            combined, combo_conflicts, combo_warnings = self.merger.combine_schemas(
                core_schema, usage_extensions=usage_exts
            )
            schema_name = self.generate_schema_name(usage_names=usage_combo)
            datapackage = self.to_datapackage(combined, schema_name=schema_name)
            self.loader.save_schema(datapackage, self.build_dir / f"{schema_name}.json")
            print(f"✓ {schema_name}.json")
            generated_count += 1

            # Get field names for CSV and store schema
            field_names = [field["name"] for field in combined.get("fields", [])]
            schemas_for_csv.append((schema_name, field_names))
            generated_schemas[schema_name] = combined

            conflicts.extend(combo_conflicts)
            warnings.extend(combo_warnings)
            if combo_conflicts:
                self._report_conflicts(schema_name, combo_conflicts)

        # 3. Each cible with all usage combinations
        for cible_name, cible_ext in cible_extensions.items():
            for usage_combo in usage_combos:
                usage_exts = (
                    [usage_extensions[name] for name in usage_combo]
                    if usage_combo
                    else None
                )
                combined, combo_conflicts, combo_warnings = self.merger.combine_schemas(
                    core_schema, usage_extensions=usage_exts, cible_extension=cible_ext
                )
                schema_name = self.generate_schema_name(
                    usage_names=usage_combo if usage_combo else None,
                    cible_name=cible_name,
                )
                datapackage = self.to_datapackage(combined, schema_name=schema_name)
                self.loader.save_schema(
                    datapackage, self.build_dir / f"{schema_name}.json"
                )
                print(f"✓ {schema_name}.json")
                generated_count += 1

                # Get field names for CSV and store schema
                field_names = [field["name"] for field in combined.get("fields", [])]
                schemas_for_csv.append((schema_name, field_names))
                generated_schemas[schema_name] = combined

                conflicts.extend(combo_conflicts)
                warnings.extend(combo_warnings)
                if combo_conflicts:
                    self._report_conflicts(schema_name, combo_conflicts)

        # Print summary
        self._print_summary(generated_count, conflicts, warnings)

        # Generate example files using examples from field definitions
        self.example_gen.generate_individual_examples(
            schemas_for_csv, generated_schemas
        )
        self.example_gen.generate_complete_example(schemas_for_csv, generated_schemas)

        return BuildResult(
            generated_count=generated_count,
            conflicts=conflicts,
            warnings=warnings,
            schemas_for_csv=schemas_for_csv,
        )

    def _report_conflicts(self, schema_name: str, schema_conflicts: List) -> None:
        """Report field conflicts for a schema."""
        print(f"\n  ⚠ CONFLICTS in {schema_name}:")
        for conflict in schema_conflicts:
            print(f"    - Field '{conflict.field_name}' has conflicting types:")
            print(f"      {conflict.source1}: {conflict.type1}")
            print(f"      {conflict.source2}: {conflict.type2}")

    def _print_summary(
        self, generated_count: int, conflicts: List, warnings: List
    ) -> None:
        """Print build summary."""
        print("\n" + "=" * 60)
        print("BUILD SUMMARY")
        print("=" * 60)

        if warnings:
            print(f"\n⚠ Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")

        if conflicts:
            print(f"\n❌ Conflicts ({len(conflicts)}):")
            for conflict in conflicts:
                print(
                    f"  - {conflict.field_name}: {conflict.source1} ({conflict.type1}) vs {conflict.source2} ({conflict.type2})"
                )
            print(
                "\nNote: Used first occurrence for conflicting fields. Please review manually."
            )
        else:
            print("\n✓ No conflicts detected!")

        print(f"\n✓ Generated {generated_count} schemas in: {self.build_dir}")
