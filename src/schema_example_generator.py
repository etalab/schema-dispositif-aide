"""Generate example CSV files for schemas."""

import csv
from pathlib import Path

import constants


class ExampleGenerator:
    """Generates example CSV files for schemas using examples from field definitions."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.examples_dir = repo_root / constants.BUILD_EXEMPLES
        self.schemas_examples_dir = repo_root / constants.BUILD_EXEMPLES_PAR_SCHEMA

    def extract_examples_from_schemas(
        self, schemas_for_csv: list[tuple[str, list[str]]], schemas: dict[str, dict]
    ) -> dict[str, str]:
        """
        Extract example values directly from schema field definitions.

        Returns a dict mapping field names to their example values from the schemas.
        """
        examples = {}

        for schema_name, field_names in schemas_for_csv:
            if schema_name not in schemas:
                continue

            schema = schemas[schema_name]
            for field in schema.get("fields", []):
                field_name = field.get("name")
                if field_name and "example" in field:
                    examples[field_name] = str(field["example"])

        return examples

    def generate_individual_examples(
        self,
        schemas_for_csv: list[tuple[str, list[str]]],
        schemas: dict[str, dict],
    ) -> None:
        """Generate a CSV file for each schema with only its fields."""
        examples = self.extract_examples_from_schemas(schemas_for_csv, schemas)
        self.schemas_examples_dir.mkdir(parents=True, exist_ok=True)

        for schema_name, field_names in schemas_for_csv:
            csv_path = self.schemas_examples_dir / constants.csv_filename(schema_name)
            missing = [f for f in field_names if f not in examples]
            if missing:
                print(
                    f"  ⚠ {schema_name}: missing example values for: {', '.join(missing)}"
                )
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=field_names)
                writer.writeheader()
                row = {field: examples.get(field, "") for field in field_names}
                writer.writerow(row)

        print(f"✓ Generated {len(schemas_for_csv)} example CSV files")

    def generate_complete_example(
        self,
        schemas_for_csv: list[tuple[str, list[str]]],
        schemas: dict[str, dict],
    ) -> None:
        """Generate a complete example CSV with all unique fields from all schemas."""
        examples = self.extract_examples_from_schemas(schemas_for_csv, schemas)

        all_fields = set()
        for schema_name, field_names in schemas_for_csv:
            all_fields.update(field_names)

        all_fields = sorted(all_fields)

        if not all_fields:
            return

        example_row = {field: examples.get(field, "") for field in all_fields}
        csv_path = self.examples_dir / constants.EXEMPLE_COMPLET_CSV

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_fields)
            writer.writeheader()
            writer.writerow(example_row)

        print(f"✓ Generated exemple-complet.csv with {len(all_fields)} fields")
