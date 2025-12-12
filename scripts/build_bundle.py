#!/usr/bin/env python3
"""
Build CompText codex bundle from YAML definitions.
"""
import argparse
import json
import hashlib
from pathlib import Path
import yaml

def load_yaml_files(codex_dir):
    """Load all YAML files from codex directory."""
    codex_path = Path(codex_dir)

    modules = []
    commands = []
    profiles = []

    for yaml_file in codex_path.glob('**/*.yaml'):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

            if 'module' in data:
                modules.append(data)
            elif 'commands' in data:
                commands.extend(data.get('commands', []))
            elif 'profile' in data:
                profiles.append(data)

    return {
        'modules': modules,
        'commands': commands,
        'profiles': profiles
    }

def build_bundle(codex_dir, output_path):
    """Build codex bundle JSON file."""
    print(f"Building bundle from {codex_dir}...")

    data = load_yaml_files(codex_dir)

    bundle = {
        'version': '1.0.0',
        'codex': data,
        'metadata': {
            'modules_count': len(data['modules']),
            'commands_count': len(data['commands']),
            'profiles_count': len(data['profiles'])
        }
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)

    # Calculate SHA-256 checksum
    with open(output, 'rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    with open(f"{output}.sha256", 'w') as f:
        f.write(f"{sha256}  {output.name}\n")

    print(f"✓ Bundle created: {output}")
    print(f"  - Modules: {bundle['metadata']['modules_count']}")
    print(f"  - Commands: {bundle['metadata']['commands_count']}")
    print(f"  - Profiles: {bundle['metadata']['profiles_count']}")
    print(f"✓ Checksum: {output}.sha256")

    return bundle

def main():
    parser = argparse.ArgumentParser(description='Build CompText codex bundle')
    parser.add_argument('--codex-dir', default='codex', help='Directory containing YAML files')
    parser.add_argument('--output', default='dist/codex.bundle.json', help='Output bundle file')

    args = parser.parse_args()

    build_bundle(args.codex_dir, args.output)

if __name__ == '__main__':
    main()
