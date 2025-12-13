#!/usr/bin/env python3
"""
Validate CompText Codex YAML files against JSON schemas.
"""
import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import validate, ValidationError
except ImportError:
    print("Error: Required packages not installed. Run: pip install pyyaml jsonschema")
    sys.exit(1)


def load_schema(schema_path):
    """Load a JSON schema file."""
    with open(schema_path, 'r') as f:
        return json.load(f)


def load_yaml_file(yaml_path):
    """Load a YAML file."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def validate_codex_file(yaml_path, schema_dir):
    """Validate a single codex YAML file."""
    data = load_yaml_file(yaml_path)

    # Determine schema based on file type
    if 'modules' in data:
        schema = load_schema(os.path.join(schema_dir, 'modules.schema.json'))
    elif 'module' in data:
        schema = load_schema(os.path.join(schema_dir, 'module_schema.json'))
    elif 'commands' in data:
        schema = load_schema(os.path.join(schema_dir, 'commands.schema.json'))
    elif 'profiles' in data:
        schema = load_schema(os.path.join(schema_dir, 'profiles.schema.json'))
    elif 'profile' in data:
        schema = load_schema(os.path.join(schema_dir, 'profile_schema.json'))
    else:
        print(f"⚠️  Unknown codex file type: {yaml_path}")
        return False

    try:
        validate(instance=data, schema=schema)
        print(f"✅ Valid: {yaml_path}")
        return True
    except ValidationError as e:
        print(f"❌ Invalid: {yaml_path}")
        print(f"   Error: {e.message}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Validate CompText Codex YAML files')
    parser.add_argument('--codex-dir', default='codex', help='Directory containing codex YAML files')
    parser.add_argument('--schema-dir', default='schemas', help='Directory containing JSON schemas')
    args = parser.parse_args()

    codex_dir = Path(args.codex_dir)
    schema_dir = Path(args.schema_dir)

    if not codex_dir.exists():
        print(f"Error: Codex directory not found: {codex_dir}")
        sys.exit(1)

    if not schema_dir.exists():
        print(f"Error: Schema directory not found: {schema_dir}")
        sys.exit(1)

    yaml_files = list(codex_dir.glob('**/*.yaml')) + list(codex_dir.glob('**/*.yml'))

    if not yaml_files:
        print(f"No YAML files found in {codex_dir}")
        sys.exit(1)

    print(f"\nValidating {len(yaml_files)} codex file(s)...\n")

    all_valid = True
    for yaml_file in yaml_files:
        if not validate_codex_file(yaml_file, schema_dir):
            all_valid = False

    print()
    if all_valid:
        print("✅ All codex files are valid!")
        sys.exit(0)
    else:
        print("❌ Some codex files are invalid.")
        sys.exit(1)


if __name__ == '__main__':
    main()
