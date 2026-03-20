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
        conflicts: List = []
        warnings: List = []
        schemas_for_csv: List[SchemaEntry] = []
        generated_schemas: Dict = {}
        known_cibles = list(cible_extensions.keys())

        # 1. Core only
        core_name = self.generate_schema_name()
        core_schema_copy = copy.deepcopy(core_schema)
        datapackage = self.to_datapackage(
            core_schema_copy, schema_name=core_name, known_cibles=known_cibles
        )
        SchemaRepository.save_schema(datapackage, self.build_dir / f"{core_name}.json")
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
            combined, c_conflicts, c_warnings = SchemaMerger.combine_schemas(
                core_schema, usage_extensions=selected_usage
            )
            schema_name = self.generate_schema_name(usage_names=usage_combination)
            self._build_and_save(
                schema_name,
                combined,
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
                combined, c_conflicts, c_warnings = SchemaMerger.combine_schemas(
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
                    combined,
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
    def to_datapackage(
        table_schema: dict, schema_name: str = None, known_cibles: list[str] = None
    ) -> dict:
        """Convert a table schema to a Frictionless data package."""
        title = "Dispositifs d'aides"
        description = table_schema.get("description", "")

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

        datapackage = {
            "name": schema_name or "dispositif-aide",
            "title": title,
            "description": description,
            "created": table_schema.get("created"),
            "lastModified": table_schema.get("lastModified"),
            "version": table_schema.get("version"),
            "countryCode": table_schema.get("countryCode"),
            "homepage": table_schema.get("homepage"),
            "licenses": table_schema.get("licenses", []),
            "contributors": table_schema.get("contributors", []),
            "sources": table_schema.get("sources", []),
            "keywords": table_schema.get("keywords", []),
            "resources": [
                {
                    "name": "validation_file",
                    "title": "Validation file",
                    "path": (
                        f"exemples/exemple-{schema_name}.csv"
                        if schema_name
                        else "exemple-complet.csv"
                    ),
                    "schema": {
                        "$schema": "https://specs.frictionlessdata.io/schemas/table-schema.json",
                        "fields": table_schema.get("fields", []),
                    },
                }
            ],
        }
        return datapackage

    def _build_and_save(
        self,
        schema_name: str,
        combined: dict,
        known_cibles: list[str],
        conflicts: list,
        warnings: list,
        schemas_for_csv: list[SchemaEntry],
        generated_schemas: dict,
        combination_conflicts: list,
        combination_warnings: list,
    ) -> None:
        """Save one schema combination and accumulate results."""
        datapackage = self.to_datapackage(
            combined, schema_name=schema_name, known_cibles=known_cibles
        )
        SchemaRepository.save_schema(
            datapackage, self.build_dir / f"{schema_name}.json"
        )
        print(f"✓ {schema_name}.json")

        field_names = [field["name"] for field in combined.get("fields", [])]
        schemas_for_csv.append((schema_name, field_names))
        generated_schemas[schema_name] = combined

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
