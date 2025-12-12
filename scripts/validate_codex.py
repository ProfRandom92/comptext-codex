#!/usr/bin/env python3
"""
Validate CompText codex YAML files against JSON schemas.
"""
import argparse
import json
import sys
from pathlib import Path
import yaml
try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema package not installed. Run: pip install jsonschema")
    sys.exit(1)

def load_schema(schema_path):
    """Load JSON schema from file."""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_yaml(yaml_path):
    """Load YAML file."""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def validate_codex_files(codex_dir, schemas_dir):
    """Validate all YAML files in codex directory."""
    codex_path = Path(codex_dir)
    schemas_path = Path(schemas_dir)

    # Define schema mappings
    schema_map = {
        'module': schemas_path / 'module_schema.json',
        'command': schemas_path / 'command_schema.json',
        'profile': schemas_path / 'profile_schema.json'
    }

    errors = []
    validated = 0

    for yaml_file in codex_path.glob('**/*.yaml'):
        try:
            data = load_yaml(yaml_file)

            # Determine schema type from file content or name
            if 'module' in data:
                schema_type = 'module'
            elif 'commands' in data:
                schema_type = 'command'
            elif 'profile' in data:
                schema_type = 'profile'
            else:
                print(f"WARNING: Cannot determine type for {yaml_file}")
                continue

            schema = load_schema(schema_map[schema_type])
            validate(instance=data, schema=schema)
            validated += 1
            print(f"✓ {yaml_file.name} validated successfully")

        except ValidationError as e:
            errors.append(f"{yaml_file}: {e.message}")
            print(f"✗ {yaml_file.name}: {e.message}")
        except Exception as e:
            errors.append(f"{yaml_file}: {str(e)}")
            print(f"✗ {yaml_file.name}: {str(e)}")

    print(f"\nValidation complete: {validated} files validated")

    if errors:
        print(f"\n{len(errors)} errors found:")
        for error in errors:
            print(f"  - {error}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description='Validate CompText codex YAML files')
    parser.add_argument('--codex-dir', default='codex', help='Directory containing YAML files')
    parser.add_argument('--schemas-dir', default='schemas', help='Directory containing JSON schemas')

    args = parser.parse_args()

    success = validate_codex_files(args.codex_dir, args.schemas_dir)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
