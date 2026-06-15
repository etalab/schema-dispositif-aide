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


class ToTableSchemaTitlingTest(unittest.TestCase):
    """Title/description must be derived from the extension objects, not by
    re-parsing the schema name (which breaks on hyphenated names like
    'secteur-public')."""

    CORE = {
        "name": "dispositif-aide",
        "path": "https://host/raw/v1/build/dispositif-aide/schema.json",
        "fields": [],
    }

    def test_hyphenated_cible_is_categorized_as_cible_not_usages(self):
        # GIVEN a cible extension whose name contains a hyphen
        table = SchemaBuilder.to_table_schema(
            self.CORE,
            schema_name="dispositif-aide-secteur-public",
            cible_extension={"name": "secteur-public"},
        )

        # THEN it is rendered as a target (hyphen shown as a space)...
        self.assertEqual(table["title"], "Dispositifs d'aides pour les secteur public")
        self.assertIn("pour la cible 'secteur public'", table["description"])
        # ...and NOT mis-labelled as usage extensions ("secteur" + "public")
        self.assertNotIn("usage", table["description"])
        self.assertNotIn("(secteur", table["title"])

    def test_hyphenated_cible_combined_with_usage(self):
        # GIVEN a hyphenated cible plus a usage extension
        table = SchemaBuilder.to_table_schema(
            self.CORE,
            schema_name="dispositif-aide-secteur-public-pilotage",
            cible_extension={"name": "secteur-public"},
            usage_extensions=[{"name": "pilotage"}],
        )

        # THEN cible and usage are each categorized correctly
        self.assertEqual(
            table["title"], "Dispositifs d'aides pour les secteur public (pilotage)"
        )
        self.assertIn("pour la cible 'secteur public'", table["description"])
        self.assertIn("avec les extensions d'usage : pilotage", table["description"])
