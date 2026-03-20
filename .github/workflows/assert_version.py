import json
import re
import os

pattern = r"v?\d+\.\d+\.\d+"


def check(obj, version, parents=""):
    """
    This functions recursively parses all fields in the schema looking for
    version names that would not be the same as the one mentioned
    in the 'version' field
    """
    errors = []
    # if field is a string, we check for a potential version
    if isinstance(obj, str):
        version_match = re.search(pattern, obj)
        if version_match and version_match[0] != version:
            errors += [(parents, version_match[0])]
    # if field is a list, we check every item
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            errors += check(item, version, parents=parents + f"[{str(idx)}]")
    # if field is a dict, we check every value
    elif isinstance(obj, dict):
        for key in obj:
            # not checking the fields
            if key != "fields":
                errors += check(
                    obj[key],
                    version,
                    parents=parents + "." + key if parents else key
                )
    return errors


SCHEMA_CORE_PATH = "schema/core/schema-core.json"

assert os.path.isfile(SCHEMA_CORE_PATH)

with open(SCHEMA_CORE_PATH, "r") as f:
    schema = json.load(f)
version = schema["version"]

errors = check(schema, version)
if errors:
    message = (
        f"Versions are mismatched within the schema '{schema['name']}', "
        f"expected version '{version}' but:"
    )
    for error_location, error_version in errors:
        message += f"\n- {error_location} has version '{error_version}'"
    raise Exception(message)
