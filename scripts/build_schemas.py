#!/usr/bin/env python3
"""
Schema Builder: Generates combined schemas from core schema and extensions.

This script generates all possible combinations where:
- Cible: none or one
- Usage: any combination of the existing extensions
"""

import sys
from pathlib import Path

# Add parent directory to path to import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.builder import SchemaBuilder


def main():
    """Main entry point."""
    try:
        SchemaBuilder().build_all_schemas()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
