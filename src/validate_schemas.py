#!/usr/bin/env python3
"""Validate all generated schemas"""

from pathlib import Path
from frictionless import validate

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
