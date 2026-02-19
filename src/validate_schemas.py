#!/usr/bin/env python3
"""Validate all generated schemas"""

from pathlib import Path
from frictionless import validate, Package

print("Validation des schémas générés...")
schemas_dir = Path("build/schemas")

if not schemas_dir.exists():
    print("❌ Aucun schéma généré. Exécutez d'abord : python3 src/build_schemas.py")
    exit(1)

valid = 0
invalid = 0

for schema_file in sorted(schemas_dir.glob("*.json")):
    try:
        report = validate(str(schema_file))
        if report.valid:
            print(f"✓ {schema_file.name}")
            valid += 1
        else:
            print(f"❌ {schema_file.name}")
            invalid += 1
            for error in report.flatten(["type", "message"]):
                print(f"   {error}")
    except Exception as e:
        print(f"❌ {schema_file.name}: {e}")
        invalid += 1

print(f"\nRésumé: {valid} valides, {invalid} invalides")

if invalid > 0:
    exit(1)

# ---------------------------------------------------------------------------
# EXPERIMENTAL: Data Package descriptor validation via frictionless.Package
#
# Package.metadata_valid checks conformance to the Frictionless Data Package
# spec (https://specs.frictionlessdata.io/data-package/): required fields
# (name, resources), valid resource paths, well-formed license/contributor
# objects, etc. It does NOT validate field types or constraint logic.
#
# Toggle with: VALIDATE_PACKAGE_DESCRIPTOR=true python3 src/validate_schemas.py
# ---------------------------------------------------------------------------
import os

if os.environ.get("VALIDATE_PACKAGE_DESCRIPTOR") == "true":
    print("\n--- Experimental: Data Package descriptor validation ---")
    pkg_valid = 0
    pkg_invalid = 0

    for schema_file in sorted(schemas_dir.glob("*.json")):
        try:
            package = Package(str(schema_file))
            errors = list(package.metadata_validate(package.to_descriptor()))
            if not errors:
                print(f"✓ {schema_file.name}")
                pkg_valid += 1
            else:
                print(f"❌ {schema_file.name}")
                pkg_invalid += 1
                for error in errors:
                    print(f"   {error}")
        except Exception as e:
            print(f"❌ {schema_file.name}: {e}")
            pkg_invalid += 1

    print(f"\nRésumé descripteur: {pkg_valid} valides, {pkg_invalid} invalides")
