"""Merge and combine schemas."""

from collections import defaultdict
from typing import Dict, List, Tuple

from src.models import FieldConflict


class SchemaMerger:
    """Handles merging of schemas and detection of conflicts."""

    def get_field_dict(self, fields: List[Dict]) -> Dict[str, Dict]:
        """Convert field list to dict keyed by field name."""
        return {field["name"]: field for field in fields}

    def get_field_type(self, field: Dict) -> str:
        """Extract the type of a field."""
        return field.get("type", "string")

    def merge_fields(
        self, fields_by_name: Dict[str, List[Tuple[str, Dict]]]
    ) -> Tuple[List[Dict], List[FieldConflict], List[str]]:
        """
        Merge fields from multiple sources.

        Returns:
            Tuple of (merged_fields, conflicts, warnings)
        """
        merged_fields = []
        conflicts = []
        warnings = []

        for field_name, sources in fields_by_name.items():
            if len(sources) == 1:
                # No conflict, take the field as is
                merged_fields.append(sources[0][1])
            else:
                # Check for type conflicts
                types = set()
                source_info = []

                for source_name, field in sources:
                    field_type = self.get_field_type(field)
                    types.add(field_type)
                    source_info.append((source_name, field_type, field))

                if len(types) == 1:
                    # All sources have same type, merge them
                    merged_field = source_info[0][2].copy()
                    merged_fields.append(merged_field)
                    warnings.append(
                        f"Field '{field_name}' found in {len(sources)} extensions with same type '{types.pop()}', merged."
                    )
                else:
                    # Type conflict
                    conflict = FieldConflict(
                        field_name=field_name,
                        source1=source_info[0][0],
                        type1=source_info[0][1],
                        source2=source_info[1][0],
                        type2=source_info[1][1],
                    )
                    conflicts.append(conflict)
                    # Keep first version
                    merged_fields.append(source_info[0][2])

        return merged_fields, conflicts, warnings

    def combine_schemas(
        self,
        core_schema: Dict,
        usage_extensions: List[Dict] = None,
        cible_extension: Dict = None,
    ) -> Tuple[Dict, List[FieldConflict], List[str]]:
        """
        Combine core schema with optional usage extensions and cible extension.

        Returns:
            Tuple of (combined_schema, conflicts, warnings)
        """
        combined = core_schema.copy()
        base_fields = self.get_field_dict(core_schema.get("fields", []))

        fields_by_name = defaultdict(list)
        for name, field in base_fields.items():
            fields_by_name[name].append(("core", field))

        # Add usage extension fields
        if usage_extensions:
            for usage_ext in usage_extensions:
                usage_fields = self.get_field_dict(usage_ext.get("fields", []))
                for name, field in usage_fields.items():
                    fields_by_name[name].append((f"usage:{usage_ext['name']}", field))

        # Add cible extension fields
        if cible_extension:
            cible_fields = self.get_field_dict(cible_extension.get("fields", []))
            for name, field in cible_fields.items():
                fields_by_name[name].append(
                    (f"cible:{cible_extension['name']}", field)
                )

        # Merge fields and check for conflicts
        merged_fields, conflicts, warnings = self.merge_fields(fields_by_name)
        combined["fields"] = merged_fields

        return combined, conflicts, warnings
