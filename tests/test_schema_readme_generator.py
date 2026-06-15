import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

import constants
from schema_readme_generator import ReadmeGenerator, _extract_sections


class ExtractSectionsTest(unittest.TestCase):
    """The section extractor walks the README line by line, toggling capture at
    each ``## `` heading depending on whether it is wanted."""

    def test_keeps_wanted_section_with_heading_and_body(self):
        md = "## Contexte\nblah\n"
        self.assertEqual(_extract_sections(md, ("Contexte",)), ["## Contexte", "blah"])

    def test_drops_unwanted_section(self):
        md = "## Contexte\nkeep\n## Format\ndrop\n"
        self.assertEqual(_extract_sections(md, ("Contexte",)), ["## Contexte", "keep"])

    def test_captures_non_contiguous_sections(self):
        # A wanted section, an unwanted one, then another wanted one: capture
        # flips on/off/on so only the two wanted blocks survive.
        md = "## Contexte\na\n## Format\nx\n## Finalité\nb\n"
        self.assertEqual(
            _extract_sections(md, ("Contexte", "Finalité")),
            ["## Contexte", "a", "## Finalité", "b"],
        )

    def test_missing_heading_yields_nothing(self):
        md = "## Format\nx\n"
        self.assertEqual(_extract_sections(md, ("Contexte",)), [])

    def test_tolerates_trailing_whitespace_on_heading(self):
        md = "## Contexte  \nbody\n"
        self.assertEqual(
            _extract_sections(md, ("Contexte",)), ["## Contexte  ", "body"]
        )

    def test_subheading_inside_section_is_body_not_boundary(self):
        # "### Sub" is not a "## " boundary, so it stays as body of its section.
        md = "## Contexte\n### Sub\nbody\n## Format\ndrop\n"
        self.assertEqual(
            _extract_sections(md, ("Contexte",)),
            ["## Contexte", "### Sub", "body"],
        )


class SharedDocGuardTest(unittest.TestCase):
    """The build must fail loudly when a required heading drifts out of the root
    README rather than silently emitting pages missing that section."""

    @staticmethod
    def _generator_for(readme_text: str, tmp: str) -> ReadmeGenerator:
        root = Path(tmp)
        (root / constants.MAIN_README).write_text(readme_text, encoding="utf-8")
        return ReadmeGenerator(root)

    def test_raises_when_a_required_section_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Only the first required section is present.
            gen = self._generator_for("## Contexte\nblah\n", tmp)
            with self.assertRaises(ValueError) as ctx:
                gen._shared_doc_section()
            # The error names the section(s) that drifted away.
            self.assertIn(constants.SHARED_README_SECTIONS[1], str(ctx.exception))

    def test_returns_all_sections_when_present(self):
        text = "\n".join(
            f"## {h}\nbody de {h}" for h in constants.SHARED_README_SECTIONS
        )
        with tempfile.TemporaryDirectory() as tmp:
            gen = self._generator_for(text, tmp)
            lines = gen._shared_doc_section()
            for h in constants.SHARED_README_SECTIONS:
                self.assertIn(f"## {h}", lines)


if __name__ == "__main__":
    unittest.main()
