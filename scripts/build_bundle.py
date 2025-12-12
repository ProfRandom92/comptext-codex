#!/usr/bin/env python3
"""
Build a single codex bundle JSON file from YAML definitions.
"""
import argparse
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


def load_yaml_files(codex_dir):
    """Load all YAML files from the codex directory."""
    codex_dir = Path(codex_dir)
    yaml_files = list(codex_dir.glob('**/*.yaml')) + list(codex_dir.glob('**/*.yml'))

    bundle = {
        'modules': [],
        'commands': [],
        'profiles': []
    }

    for yaml_file in yaml_files:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

            if 'modules' in data:
                bundle['modules'].extend(data['modules'])
            if 'commands' in data:
                bundle['commands'].extend(data['commands'])
            if 'profiles' in data:
                bundle['profiles'].extend(data['profiles'])

    return bundle


def main():
    parser = argparse.ArgumentParser(description='Build CompText Codex bundle')
    parser.add_argument('--codex-dir', default='codex', help='Directory containing codex YAML files')
    parser.add_argument('--output', default='dist/codex.bundle.json', help='Output bundle file path')
    args = parser.parse_args()

    codex_dir = Path(args.codex_dir)
    output_path = Path(args.output)

    if not codex_dir.exists():
        print(f"Error: Codex directory not found: {codex_dir}")
        sys.exit(1)

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Building codex bundle from {codex_dir}...")

    bundle = load_yaml_files(codex_dir)

    print(f"  Modules: {len(bundle['modules'])}")
    print(f"  Commands: {len(bundle['commands'])}")
    print(f"  Profiles: {len(bundle['profiles'])}")

    # Write bundle
    with open(output_path, 'w') as f:
        json.dump(bundle, f, indent=2)

    print(f"\n✅ Bundle written to {output_path}")
    print(f"   Size: {output_path.stat().st_size} bytes")


if __name__ == '__main__':
    main()
