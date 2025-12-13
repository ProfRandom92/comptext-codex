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
    parser.add_argument('--out', dest='out', default=None, help='Output bundle file path')
    parser.add_argument('--output', dest='output', default=None, help='(deprecated) Output bundle file path (use --out)')
    parser.add_argument('--version', default='unknown', help='Bundle version identifier')
    args = parser.parse_args()

    codex_dir = Path(args.codex_dir)
    if args.out and args.output:
        print("Warning: both --out and deprecated --output provided; using --out value.")
    elif args.output and not args.out:
        print("Warning: --output is deprecated; prefer --out instead.")

    output_path = Path(args.out or args.output or 'dist/codex.bundle.json')

    if not codex_dir.exists():
        print(f"Error: Codex directory not found: {codex_dir}")
        sys.exit(1)

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Building codex bundle from {codex_dir} (version: {args.version})...")

    bundle = load_yaml_files(codex_dir)
    bundle['version'] = args.version

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
