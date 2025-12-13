#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
try:
    import yaml
except Exception:
    print("PyYAML is required. Install: pip install pyyaml", file=sys.stderr)
    raise
try:
    import jsonschema
except Exception:
    print("jsonschema is required. Install: pip install jsonschema", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"

def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def validate(instance, schema_path: Path):
    schema = load_json(schema_path)
    jsonschema.validate(instance=instance, schema=schema)

def read_yaml(p: Path):
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{p} must be a YAML object.")
    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codex-dir", default="codex")
    args = ap.parse_args()

    codex = (ROOT / args.codex_dir).resolve()
    if not codex.exists():
        raise SystemExit(f"codex dir not found: {codex}")

    module_schema = SCHEMAS / "module.schema.json"
    command_schema = SCHEMAS / "command.schema.json"
    profile_schema = SCHEMAS / "profile.schema.json"

    errors = 0
    for p in sorted((codex / "modules").glob("*.yaml")):
        try:
            validate(read_yaml(p), module_schema)
        except Exception as e:
            errors += 1
            print(f"[MODULE INVALID] {p}: {e}", file=sys.stderr)
    for p in sorted((codex / "commands").glob("*.yaml")):
        try:
            validate(read_yaml(p), command_schema)
        except Exception as e:
            errors += 1
            print(f"[COMMAND INVALID] {p}: {e}", file=sys.stderr)
    for p in sorted((codex / "profiles").glob("*.yaml")):
        try:
            validate(read_yaml(p), profile_schema)
        except Exception as e:
            errors += 1
            print(f"[PROFILE INVALID] {p}: {e}", file=sys.stderr)

    if errors:
        raise SystemExit(f"Validation failed: {errors} file(s) invalid.")
    print("Validation OK.")

if __name__ == "__main__":
    main()
