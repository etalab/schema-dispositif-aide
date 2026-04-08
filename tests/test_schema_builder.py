import os
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

        # THEN generated schemas must match expected schemas
        expected_path = Path(__file__).parent / "expected" / "schemas"
        self.assertListEqual(sorted(os.listdir(expected_path)), sorted(os.listdir(builder.build_dir)))
