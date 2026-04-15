#!/usr/bin/env python3
"""Validate all generated schemas and their example CSV files."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import constants
from frictionless import validate

schemas_dir = constants.BUILD_SCHEMAS
root_datapackage = constants.DATAPACKAGE

if not schemas_dir.exists():
    print("❌ Aucun schéma généré. Exécutez d'abord : python3 src/build_schemas.py")
    exit(1)

valid = 0
invalid = 0


def check(report, label: str) -> None:
    global valid, invalid
    if report.valid:
        print(f"✓ {label}")
        valid += 1
    else:
        print(f"❌ {label}")
        for error in report.flatten(["type", "message"]):
            print(f"   {error}")
        invalid += 1


print("--- Validation de l'ensemble du datapackage ---")
if not root_datapackage.exists():
    print(f"❌ {root_datapackage}: fichier introuvable")
    invalid += 1
else:
    try:
        check(validate(str(root_datapackage)), root_datapackage.name)
    except Exception as e:
        print(f"❌ {root_datapackage}: {e}")
        invalid += 1

print("\n--- Détail des validations des schémas ---")
for schema_file in sorted(schemas_dir.glob("*.json")):
    try:
        check(validate(str(schema_file), type="schema"), schema_file.name)
    except Exception as e:
        print(f"❌ {schema_file.name}: {e}")
        invalid += 1

print("\n--- Détail des validations des exemples CSV contre leur schéma ---")
for schema_file in sorted(schemas_dir.glob("*.json")):
    csv_file = constants.BUILD_EXEMPLES_PAR_SCHEMA / constants.csv_filename(
        schema_file.stem
    )
    if not csv_file.exists():
        print(f"❌ {csv_file.name}: fichier exemple introuvable")
        invalid += 1
        continue
    try:
        check(validate(str(csv_file), schema=str(schema_file)), csv_file.name)
    except Exception as e:
        print(f"❌ {csv_file.name}: {e}")
        invalid += 1

print(f"\nRésumé: {valid} tests valides, {invalid} invalides")
if invalid > 0:
    exit(1)
