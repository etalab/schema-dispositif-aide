import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from schema_merger import SchemaMerger


def _contributor(title, email):
    return {"title": title, "email": email, "role": "contributor"}


def _field(name):
    return {"name": name, "title": name, "type": "string"}


class SchemaMergerContributorsTest(unittest.TestCase):
    def _core(self):
        return {
            "name": "dispositif-aide",
            "title": "Dispositifs d'aides",
            "description": "Schéma de base.",
            "contributors": [
                _contributor("Core One", "one@core"),
                _contributor("Core Two", "two@core"),
            ],
            "fields": [_field("id"), _field("nom")],
        }

    def test_extension_contributors_replace_core(self):
        # GIVEN a core (technical contributors) and a cible extension declaring metier contributors
        core = self._core()
        cible = {
            "name": "professionnels",
            "contributors": [_contributor("Metier Author", "author@ext")],
            "fields": [_field("base_juridique")],
        }

        # WHEN combining them
        merged, _conflicts, _warnings = SchemaMerger.combine_schemas(
            core, cible_extension=cible
        )

        # THEN the core contributors are replaced, not extended
        self.assertEqual(
            [c["title"] for c in merged["contributors"]],
            ["Metier Author"],
        )

    def test_core_contributors_kept_when_extension_defines_none(self):
        # GIVEN a core with contributors and a cible extension that declares none
        core = self._core()
        cible = {
            "name": "professionnels",
            "fields": [_field("base_juridique")],
        }

        # WHEN combining them
        merged, _conflicts, _warnings = SchemaMerger.combine_schemas(
            core, cible_extension=cible
        )

        # THEN the core contributors stand as the fallback
        self.assertEqual(
            [c["title"] for c in merged["contributors"]],
            ["Core One", "Core Two"],
        )

    def test_contributors_from_several_extensions_are_unioned_and_deduped(self):
        # GIVEN a usage and a cible extension that both declare contributors, with an overlap
        core = self._core()
        usage = {
            "name": "activation",
            "contributors": [_contributor("Metier A", "a@ext")],
            "fields": [_field("activation_field")],
        }
        cible = {
            "name": "professionnels",
            "contributors": [
                _contributor("Metier A (dup)", "a@ext"),  # same email as usage's
                _contributor("Metier B", "b@ext"),
            ],
            "fields": [_field("base_juridique")],
        }

        # WHEN combining them
        merged, _conflicts, _warnings = SchemaMerger.combine_schemas(
            core, usage_extensions=[usage], cible_extension=cible
        )

        # THEN core is replaced by the deduped union of extension contributors (first occurrence wins)
        self.assertEqual(
            [c["title"] for c in merged["contributors"]],
            ["Metier A", "Metier B"],
        )

    def test_contributors_do_not_leak_into_fields(self):
        # GIVEN a core and a cible extension, both carrying contributors
        core = self._core()
        cible = {
            "name": "professionnels",
            "contributors": [_contributor("Metier Author", "author@ext")],
            "fields": [_field("base_juridique")],
        }

        # WHEN combining them
        merged, _conflicts, _warnings = SchemaMerger.combine_schemas(
            core, cible_extension=cible
        )

        # THEN fields are exactly core + extension fields, with no phantom "contributors" field
        field_names = [f["name"] for f in merged["fields"]]
        self.assertEqual(field_names, ["id", "nom", "base_juridique"])
        self.assertNotIn("contributors", field_names)

    def test_nothing_but_fields_and_contributors_changes(self):
        # GIVEN a core schema with extra top-level metadata
        core = self._core()
        cible = {
            "name": "professionnels",
            "contributors": [_contributor("Metier Author", "author@ext")],
            "fields": [_field("base_juridique")],
        }

        # WHEN combining them
        merged, _conflicts, _warnings = SchemaMerger.combine_schemas(
            core, cible_extension=cible
        )

        # THEN every other top-level key is untouched (only fields/contributors differ)
        for key in core:
            if key in ("fields", "contributors"):
                continue
            self.assertEqual(merged[key], core[key], f"top-level key '{key}' changed")

    def test_contributors_absent_when_no_source_declares_any(self):
        # GIVEN a core and extension that declare no contributors at all
        core = {"name": "core", "fields": [_field("id")]}
        cible = {"name": "ext", "fields": [_field("extra")]}

        # WHEN combining them
        merged, _conflicts, _warnings = SchemaMerger.combine_schemas(
            core, cible_extension=cible
        )

        # THEN no empty "contributors" key is introduced
        self.assertNotIn("contributors", merged)


if __name__ == "__main__":
    unittest.main()
