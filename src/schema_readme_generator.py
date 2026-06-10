"""Generate a README.md homepage for each built schema.

On schema.data.gouv.fr, each schema directory's README.md is rendered as the
landing page. We build a short page from the schema's own title/description and
the titles/descriptions of the extensions it combines.
"""

from pathlib import Path

import constants


def _is_required(field: dict) -> bool:
    return bool(field.get("constraints", {}).get("required"))


def _escape_cell(value: str) -> str:
    """Make a string safe to drop in a Markdown table cell."""
    return value.replace("\n", " ").replace("|", "\\|").strip()


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
        lines += self._main_readme_section()
        lines += self._fields_section(schema.get("fields", []))
        lines += self._resources_section()

        return "\n".join(lines).rstrip() + "\n"

    def _main_readme_section(self) -> list[str]:
        # No link: a hyperlink would point to GitHub and break once the schema is
        # published on schema.data.gouv.fr, so we refer to the root README in
        # words instead.
        base = constants.BASE_TITLE.lower()
        return [
            f"> 📖 **À propos** — Ce schéma fait partie d'un ensemble de schémas "
            f"décrivant les {base} selon leur cible et pour différents usages. "
            "Pour le contexte et la finalité de l'ensemble, consultez la documentation "
            "principale.",
            "",
        ]

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

    def _fields_section(self, fields: list[dict]) -> list[str]:
        lines = [
            f"## Champs ({len(fields)})",
            "",
            "| Champ | Libellé | Type | Obligatoire |",
            "| --- | --- | --- | --- |",
        ]
        for field in fields:
            name = field.get("name", "")
            label = _escape_cell(field.get("title", ""))
            ftype = field.get("type", "string")
            required = "Oui" if _is_required(field) else "Non"
            lines.append(f"| `{name}` | {label} | {ftype} | {required} |")
        lines.append("")
        return lines

    def _resources_section(self) -> list[str]:
        return [
            "## Ressources",
            "",
            f"- Schéma : [`{constants.SCHEMA_FILENAME}`]({constants.SCHEMA_FILENAME})",
            f"- Exemple valide : [`{constants.EXEMPLE_FILENAME}`]({constants.EXEMPLE_FILENAME})",
            "",
        ]
