#!/usr/bin/env python3
"""Validate all generated schemas and their example CSV files."""

from pathlib import Path
from frictionless import validate

schemas_dir = Path("build/schemas")
examples_dir = schemas_dir / "exemples"
root_datapackage = Path("datapackage.json")

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
    csv_file = examples_dir / f"exemple-{schema_file.stem}.csv"
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
