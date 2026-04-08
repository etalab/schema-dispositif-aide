#!/usr/bin/env python3
"""
Script that generates combined schemas from core schema and extensions.

It generates all possible combinations where:
- Cible: none or one
- Usage: any combination of the existing extensions
"""

import sys
from pathlib import Path

from schema_builder import SchemaBuilder


def main():
    """Main entry point."""
    try:
        SchemaBuilder(Path(__file__).parent.parent).build_all_schemas()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
