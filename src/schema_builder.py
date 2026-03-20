"""Main schema builder orchestrator."""

import copy
from itertools import combinations, chain
from pathlib import Path

from models import BuildResult, SchemaEntry
from schema_repository import SchemaRepository
from schema_merger import SchemaMerger
from schema_example_generator import ExampleGenerator


class SchemaBuilder:
    """Orchestrates the schema building process."""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.repository = SchemaRepository(self.repo_root)
        self.example_gen = ExampleGenerator(self.repo_root)
        self.build_dir = self.repo_root / "build" / "schemas"

    def build_all_schemas(self) -> BuildResult:
        """Build all schema combinations."""

        core_schema = self.repository.load_core_schema()
        usage_extensions = self.repository.load_extensions("usage")
        cible_extensions = self.repository.load_extensions("cible")
        print(
            f"Found {len(usage_extensions)} usage extensions: {list(usage_extensions.keys())}"
        )
        print(
            f"Found {len(cible_extensions)} cible extensions: {list(cible_extensions.keys())}"
        )

        usage_combinations = self.get_usage_combinations(usage_extensions)
        print(
            f"Will generate {len(usage_combinations)*(len(cible_extensions)+1)} schemas"
        )

        # Clean build directory
        self.build_dir.mkdir(parents=True, exist_ok=True)
        for json_file in self.build_dir.glob("*.json"):
            json_file.unlink()

        # Generate schemas
        conflicts: list = []
        warnings: list = []
        schemas_for_csv: list[SchemaEntry] = []
        generated_schemas: dict = {}
        known_cibles = list(cible_extensions.keys())

        # 1. Core only
        core_name = self.generate_schema_name()
        core_schema_copy = copy.deepcopy(core_schema)
        table_schema = SchemaBuilder.to_table_schema(
            core_schema_copy, schema_name=core_name, known_cibles=known_cibles
        )
        SchemaRepository.save_schema(table_schema, self.build_dir / f"{core_name}.json")
        print(f"✓ {core_name}.json")
        core_field_names = [
            field["name"] for field in core_schema_copy.get("fields", [])
        ]
        schemas_for_csv.append((core_name, core_field_names))
        generated_schemas[core_name] = core_schema_copy

        # 2. Core + usage combinations (no cible)
        for usage_combination in usage_combinations:
            if not usage_combination:
                continue
            selected_usage = [usage_extensions[name] for name in usage_combination]
            merged_schema, c_conflicts, c_warnings = SchemaMerger.combine_schemas(
                core_schema, usage_extensions=selected_usage
            )
            schema_name = self.generate_schema_name(usage_names=usage_combination)
            self._build_and_save(
                schema_name,
                merged_schema,
                known_cibles,
                conflicts,
                warnings,
                schemas_for_csv,
                generated_schemas,
                c_conflicts,
                c_warnings,
            )

        # 3. Each cible × all usage combinations
        for cible_name, cible_extension in cible_extensions.items():
            for usage_combination in usage_combinations:
                selected_usage = (
                    [usage_extensions[name] for name in usage_combination]
                    if usage_combination
                    else None
                )
                merged_schema, c_conflicts, c_warnings = SchemaMerger.combine_schemas(
                    core_schema,
                    usage_extensions=selected_usage,
                    cible_extension=cible_extension,
                )
                schema_name = self.generate_schema_name(
                    usage_names=usage_combination or None,
                    cible_name=cible_name,
                )
                self._build_and_save(
                    schema_name,
                    merged_schema,
                    known_cibles,
                    conflicts,
                    warnings,
                    schemas_for_csv,
                    generated_schemas,
                    c_conflicts,
                    c_warnings,
                )

        generated_count = len(schemas_for_csv)

        # Print summary
        self._print_summary(generated_count, conflicts, warnings)

        # Generate example files using examples from field definitions
        self.example_gen.generate_individual_examples(
            schemas_for_csv, generated_schemas
        )
        self.example_gen.generate_complete_example(schemas_for_csv, generated_schemas)

        # Generate root datapackage.json
        self._generate_root_datapackage(schemas_for_csv)

        return BuildResult(
            generated_count=generated_count,
            conflicts=conflicts,
            warnings=warnings,
            schemas_for_csv=schemas_for_csv,
        )

    @staticmethod
    def get_usage_combinations(usage_extensions: dict) -> list[tuple]:
        """Generate all combinations of usage extensions (0 or more)."""
        usage_names = list(usage_extensions.keys())
        return list(
            chain.from_iterable(
                combinations(usage_names, size)
                for size in range(len(usage_names) + 1)
            )
        )

    @staticmethod
    def generate_schema_name(
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

    @staticmethod
    def to_table_schema(
        merged_schema: dict, schema_name: str = None, known_cibles: list[str] = None
    ) -> dict:
        """
        Adjust a merged schema into a final table schema.

        The input is already a valid table schema (deep copy of core with merged fields).
        This method only overrides the fields that needs to be reedited per generated schema:
        - name, title, description, resources, path
        """
        name = schema_name or "dispositif-aide"
        title = "Dispositifs d'aides"
        description = merged_schema.get("description", "")

        if schema_name and schema_name != "dispositif-aide":
            parts = schema_name.replace("dispositif-aide-", "").split("-")
            cible_part = None
            usage_parts = []

            if parts and known_cibles and parts[0] in known_cibles:
                cible_part = parts[0]
                usage_parts = parts[1:]
            else:
                usage_parts = parts

            title_parts = ["Dispositifs d'aides"]
            if cible_part:
                title_parts.append(f"pour les {cible_part}")
            if usage_parts:
                title_parts.append(f"({', '.join(usage_parts)})")
            title = " ".join(title_parts)

            if cible_part or usage_parts:
                description_parts = ["Extension du schéma dispositif-aide"]
                if cible_part:
                    description_parts.append(f"pour la cible '{cible_part}'")
                if usage_parts:
                    description_parts.append(
                        f"avec les extensions d'usage : {', '.join(usage_parts)}"
                    )
                description = " ".join(description_parts)

        table_schema = copy.deepcopy(merged_schema)
        table_schema["name"] = name
        table_schema["title"] = title
        table_schema["description"] = description
        table_schema["resources"] = [
            {
                "title": "Fichier de validation (CSV)",
                "name": f"exemple-{name}-csv",
                "path": f"exemples/exemple-{name}.csv",
            }
        ]
        base_url = merged_schema.get("path", "").rsplit("/", 1)[0]
        table_schema["path"] = f"{base_url}/{name}.json"
        return table_schema

    def _build_and_save(
        self,
        schema_name: str,
        merged_schema: dict,
        known_cibles: list[str],
        conflicts: list,
        warnings: list,
        schemas_for_csv: list[SchemaEntry],
        generated_schemas: dict,
        combination_conflicts: list,
        combination_warnings: list,
    ) -> None:
        """Save one schema combination and accumulate results."""
        table_schema = SchemaBuilder.to_table_schema(
            merged_schema, schema_name=schema_name, known_cibles=known_cibles
        )
        SchemaRepository.save_schema(
            table_schema, self.build_dir / f"{schema_name}.json"
        )
        print(f"✓ {schema_name}.json")

        field_names = [field["name"] for field in merged_schema.get("fields", [])]
        schemas_for_csv.append((schema_name, field_names))
        generated_schemas[schema_name] = merged_schema

        conflicts.extend(combination_conflicts)
        warnings.extend(combination_warnings)
        if combination_conflicts:
            self._report_conflicts(schema_name, combination_conflicts)

    def _report_conflicts(self, schema_name: str, schema_conflicts: list) -> None:
        """Report field conflicts for a schema."""
        print(f"\n  ⚠ CONFLICTS in {schema_name}:")
        for conflict in schema_conflicts:
            print(f"    - Field '{conflict.field_name}' has conflicting types:")
            print(f"      {conflict.source1}: {conflict.type1}")
            print(f"      {conflict.source2}: {conflict.type2}")

    def _generate_root_datapackage(self, schemas_for_csv: list[SchemaEntry]) -> None:
        """Generate root-level datapackage.json listing all generated schemas."""
        resources = [
            {
                "name": schema_name,
                "path": f"build/schemas/exemples/exemple-{schema_name}.csv",
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": f"build/schemas/{schema_name}.json",
                "documentation": "README.md",
            }
            for schema_name, _ in schemas_for_csv
        ]
        datapackage = {
            "name": "schemas-dispositif-aide",
            "title": "Schémas des dispositifs d'aide",
            "description": "Schémas de données permettant de décrire plus ou moins précisément les dispositifs d'aide",
            "id": "schemas-dispositif-aide",
            "resources": resources,
        }
        SchemaRepository.save_schema(datapackage, self.repo_root / "datapackage.json")
        print("✓ datapackage.json")

    def _print_summary(
        self, generated_count: int, conflicts: list, warnings: list
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

        print(f"\n✓ Generated {generated_count} schemas")
