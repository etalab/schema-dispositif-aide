"""Generate example CSV files for schemas."""

import csv
from pathlib import Path
from typing import Dict, List, Tuple


class ExampleGenerator:
    """Generates example CSV files for schemas using examples from field definitions."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.examples_dir = repo_root / "build" / "schemas" / "exemples"

    def extract_examples_from_schemas(
        self, schemas_for_csv: List[Tuple[str, List[str]]], schemas: Dict[str, Dict]
    ) -> Dict[str, str]:
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
                    # Use the example from the field definition
                    examples[field_name] = str(field["example"])

        return examples

    def generate_individual_examples(
        self,
        schemas_for_csv: List[Tuple[str, List[str]]],
        schemas: Dict[str, Dict],
    ) -> None:
        """Generate a CSV file for each schema with only its fields."""
        examples = self.extract_examples_from_schemas(schemas_for_csv, schemas)
        self.examples_dir.mkdir(parents=True, exist_ok=True)

        for schema_name, field_names in schemas_for_csv:
            csv_path = self.examples_dir / f"exemple-{schema_name}.csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=field_names)
                writer.writeheader()
                row = {field: examples.get(field, "") for field in field_names}
                writer.writerow(row)
            print(f"  ✓ {csv_path.name} ({len(field_names)} fields)")

        print(f"✓ Generated {len(schemas_for_csv)} example CSV files")

    def generate_complete_example(
        self,
        schemas_for_csv: List[Tuple[str, List[str]]],
        schemas: Dict[str, Dict],
    ) -> None:
        """Generate a complete example CSV with all unique fields from all schemas."""
        examples = self.extract_examples_from_schemas(schemas_for_csv, schemas)

        # Collect all unique field names
        all_fields = set()
        for schema_name, field_names in schemas_for_csv:
            all_fields.update(field_names)

        all_fields = sorted(list(all_fields))

        if not all_fields:
            return

        example_row = {field: examples.get(field, "") for field in all_fields}
        csv_path = self.repo_root / "exemple-complet.csv"

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_fields)
            writer.writeheader()
            writer.writerow(example_row)

        print(f"✓ Generated exemple-complet.csv with {len(all_fields)} fields")
