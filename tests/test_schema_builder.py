import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from schema_builder import SchemaBuilder


class SchemaBuilderTest(unittest.TestCase):
    def test_schemas_are_built(self):
        # GIVEN a source schemas directory
        builder = SchemaBuilder(Path(__file__).parent)
        self.assertTrue(builder.repository.core_path.exists())

        # WHEN building the schemas
        builder.build_all_schemas()

        # THEN one directory per schema is generated, matching the expected set
        expected_path = Path(__file__).parent / "expected"
        expected_names = sorted(p.name for p in expected_path.iterdir() if p.is_dir())
        built_names = sorted(p.name for p in builder.build_dir.iterdir() if p.is_dir())
        self.assertListEqual(expected_names, built_names)

        # AND each schema directory holds its schema, README homepage and example
        for name in expected_names:
            schema_dir = builder.build_dir / name
            self.assertTrue((schema_dir / "schema.json").exists(), f"{name}/schema.json")
            self.assertTrue((schema_dir / "README.md").exists(), f"{name}/README.md")
            self.assertTrue((schema_dir / "exemple.csv").exists(), f"{name}/exemple.csv")
