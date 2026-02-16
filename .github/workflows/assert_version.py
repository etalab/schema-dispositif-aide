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


to_check = []

if "schema.json" in os.listdir():
    to_check.append("schema.json")

elif "datapackage.json" in os.listdir():
    with open("datapackage.json", "r") as f:
        datapackage = json.load(f)
    for resource in datapackage["resources"]:
        to_check.append(resource["schema"])

else:
    raise Exception("No required file found")

for schema_path in to_check:
    with open(schema_path, "r") as f:
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
