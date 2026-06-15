"""Generate a README.md homepage for each built schema.

On schema.data.gouv.fr, each schema directory's README.md is rendered as the
landing page. We build a page from the schema's own title/description, the
extensions it combines, and the shared context/finality/management sections
copied verbatim from the root README so each schema reads as a self-contained
document.
"""

from pathlib import Path

import constants


class ReadmeGenerator:
    """Writes a Markdown homepage for one built schema."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def generate(
        self, schema_name: str, table_schema: dict, extensions: list[dict]
    ) -> None:
        """Render and write the README for a single built schema."""
        path = self.repo_root / constants.readme_path(schema_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._render(table_schema, extensions), encoding="utf-8")

    def _render(self, schema: dict, extensions: list[dict]) -> str:
        title = schema.get("title", constants.BASE_TITLE)
        description = schema.get("description", "").strip()

        lines = [f"# {title}", ""]
        if description:
            lines += [description, ""]

        lines += self._composition_section(extensions)
        lines += self._shared_doc_section()

        return "\n".join(lines).rstrip() + "\n"

    def _composition_section(self, extensions: list[dict]) -> list[str]:
        if not extensions:
            return [
                "## Composition",
                "",
                f"Ce schéma correspond au socle commun « {constants.BASE_TITLE} », "
                "sans extension.",
                "",
            ]

        lines = [
            "## Composition",
            "",
            f"Ce schéma enrichit le socle commun « {constants.BASE_TITLE} » "
            "avec les extensions suivantes :",
            "",
        ]
        for ext in extensions:
            ext_title = ext.get("title") or ext.get("name", "")
            ext_desc = ext.get("description", "").strip()
            if ext_desc:
                lines.append(f"- **{ext_title}** — {ext_desc}")
            else:
                lines.append(f"- **{ext_title}**")
        lines.append("")
        return lines

    def _shared_doc_section(self) -> list[str]:
        """Copy the context/finality/management sections from the root README so
        each schema page carries the shared documentation inline.

        Raises if a required section can't be found, so a renamed/retyped heading
        in the root README fails the build loudly instead of silently dropping
        the section from every generated page.
        """
        readme = self.repo_root / constants.MAIN_README
        try:
            content = readme.read_text(encoding="utf-8")
        except FileNotFoundError:
            return []
        lines = _extract_sections(content, constants.SHARED_README_SECTIONS)
        found = {line[3:].strip() for line in lines if line.startswith("## ")}
        missing = [h for h in constants.SHARED_README_SECTIONS if h not in found]
        if missing:
            raise ValueError(
                f"Sections introuvables dans {constants.MAIN_README} : "
                f"{', '.join(missing)}. Les titres doivent correspondre "
                "exactement à constants.SHARED_README_SECTIONS."
            )
        return lines


def _extract_sections(markdown: str, headings: tuple[str, ...]) -> list[str]:
    """Return the lines of the ``## <heading>`` sections named in ``headings``,
    in the order they appear in ``markdown``, including the heading lines."""
    out: list[str] = []
    capturing = False
    for line in markdown.splitlines():
        if line.startswith("## "):
            capturing = line[3:].strip() in headings
        if capturing:
            out.append(line)
    return out
