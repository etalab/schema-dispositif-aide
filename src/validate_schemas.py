#!/usr/bin/env python3
"""Validate all generated schemas and their example CSV files."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import constants
from frictionless import validate

build_dir = constants.BUILD_DIR
root_datapackage = constants.DATAPACKAGE

# Each schema lives in build/<name>/schema.json alongside its exemple.csv.
schema_files = sorted(build_dir.glob(f"*/{constants.SCHEMA_FILENAME}"))

if not schema_files:
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
for schema_file in schema_files:
    label = f"{schema_file.parent.name}/{schema_file.name}"
    try:
        check(validate(str(schema_file), type="schema"), label)
    except Exception as e:
        print(f"❌ {label}: {e}")
        invalid += 1

print("\n--- Détail des validations des exemples CSV contre leur schéma ---")
for schema_file in schema_files:
    csv_file = schema_file.parent / constants.EXEMPLE_FILENAME
    label = f"{schema_file.parent.name}/{csv_file.name}"
    if not csv_file.exists():
        print(f"❌ {label}: fichier exemple introuvable")
        invalid += 1
        continue
    try:
        check(validate(str(csv_file), schema=str(schema_file)), label)
    except Exception as e:
        print(f"❌ {label}: {e}")
        invalid += 1

print(f"\nRésumé: {valid} tests valides, {invalid} invalides")
if invalid > 0:
    exit(1)
