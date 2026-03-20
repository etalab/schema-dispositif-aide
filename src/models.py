"""Data models for schema building."""

from dataclasses import dataclass

SchemaEntry = tuple[str, list[str]]


@dataclass
class FieldConflict:
    """Represents a conflict between fields in different schemas."""

    field_name: str
    source1: str
    type1: str
    source2: str
    type2: str


@dataclass
class BuildResult:
    """Result of a build operation."""

    generated_count: int
    conflicts: list[FieldConflict]
    warnings: list[str]
    schemas_for_csv: list[SchemaEntry]
