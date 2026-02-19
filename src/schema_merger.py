"""Merge and combine schemas."""

import copy
from collections import defaultdict
from typing import Dict, List, Tuple

from models import FieldConflict


class SchemaMerger:
    """Handles merging of schemas and detection of conflicts."""

    @staticmethod
    def get_field_dict(fields: List[Dict]) -> Dict[str, Dict]:
        """Convert field list to dict keyed by field name."""
        return {field["name"]: field for field in fields}

    @staticmethod
    def get_field_type(field: Dict) -> str:
        """Extract the type of a field."""
        return field.get("type", "string")

    @staticmethod
    def merge_constraints(
        field_name: str, sources_constraints: List[Tuple[str, Dict]]
    ) -> Tuple[Dict, List[str]]:
        """
        Merge constraints from multiple sources of the same field.

        Strategy:
        - required, unique: True wins (most restrictive)
        - maxLength, maximum, maximumLength: minimum value wins (most restrictive)
        - minLength, minimum, minimumLength: maximum value wins (most restrictive)
        - enum: intersection; warns and keeps first if result is empty
        - pattern: kept from first source; warns if sources differ
        - Other keys: first source wins; warns if sources differ
        """
        merged = {}
        warnings = []

        all_keys = set()
        for _, c in sources_constraints:
            all_keys.update(c.keys())

        for key in all_keys:
            values = [(src, c[key]) for src, c in sources_constraints if key in c]

            if len(values) == 1:
                merged[key] = values[0][1]
                continue

            if key in ("required", "unique"):
                merged[key] = any(v for _, v in values)

            elif key in ("maxLength", "maximum", "maximumLength"):
                merged[key] = min(v for _, v in values)

            elif key in ("minLength", "minimum", "minimumLength"):
                merged[key] = max(v for _, v in values)

            elif key == "enum":
                sets = [set(v) for _, v in values]
                intersection = sets[0].intersection(*sets[1:])
                if not intersection:
                    warnings.append(
                        f"Field '{field_name}': constraint 'enum' has empty intersection across sources, keeping first source."
                    )
                    merged[key] = values[0][1]
                else:
                    merged[key] = sorted(intersection)

            elif key == "pattern":
                unique_patterns = list(dict.fromkeys(v for _, v in values))
                if len(unique_patterns) > 1:
                    warnings.append(
                        f"Field '{field_name}': constraint 'pattern' differs across sources {[s for s, _ in values]}, keeping first."
                    )
                merged[key] = values[0][1]

            else:
                unique_values = list(dict.fromkeys(str(v) for _, v in values))
                if len(unique_values) > 1:
                    warnings.append(
                        f"Field '{field_name}': constraint '{key}' differs across sources {[s for s, _ in values]}, keeping first."
                    )
                merged[key] = values[0][1]

        return merged, warnings

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
                    field_type = SchemaMerger.get_field_type(field)
                    types.add(field_type)
                    source_info.append((source_name, field_type, field))

                if len(types) == 1:
                    # Same type: start from first source and merge constraints
                    merged_field = copy.deepcopy(source_info[0][2])
                    sources_constraints = [
                        (src, f.get("constraints", {}))
                        for src, _, f in source_info
                        if f.get("constraints")
                    ]
                    if sources_constraints:
                        merged_constraints, constraint_warnings = (
                            self.merge_constraints(field_name, sources_constraints)
                        )
                        merged_field["constraints"] = merged_constraints
                        warnings.extend(constraint_warnings)
                    merged_fields.append(merged_field)
                else:
                    # Type conflict: keep first, report
                    conflict = FieldConflict(
                        field_name=field_name,
                        source1=source_info[0][0],
                        type1=source_info[0][1],
                        source2=source_info[1][0],
                        type2=source_info[1][1],
                    )
                    conflicts.append(conflict)
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
        combined = copy.deepcopy(core_schema)
        base_fields = SchemaMerger.get_field_dict(core_schema.get("fields", []))

        fields_by_name = defaultdict(list)
        for name, field in base_fields.items():
            fields_by_name[name].append(("core", field))

        # Add usage extension fields
        if usage_extensions:
            for usage_ext in usage_extensions:
                usage_fields = SchemaMerger.get_field_dict(usage_ext.get("fields", []))
                for name, field in usage_fields.items():
                    fields_by_name[name].append((f"usage:{usage_ext['name']}", field))

        # Add cible extension fields
        if cible_extension:
            cible_fields = SchemaMerger.get_field_dict(cible_extension.get("fields", []))
            for name, field in cible_fields.items():
                fields_by_name[name].append(
                    (f"cible:{cible_extension['name']}", field)
                )

        # Merge fields and check for conflicts
        merged_fields, conflicts, warnings = self.merge_fields(fields_by_name)
        combined["fields"] = merged_fields

        return combined, conflicts, warnings
