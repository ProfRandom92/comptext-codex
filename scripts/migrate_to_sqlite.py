#!/usr/bin/env python3
"""Migrate YAML definitions and Notion CSV export into the SQLite CodexStore.

Usage:
    python scripts/migrate_to_sqlite.py [--codex-dir codex] [--csv data/CompText-Codex.csv] [--db codex.db]

This script is idempotent: running it multiple times will upsert without
creating duplicates.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

from comptext_codex.store import CodexStore


# -- YAML migration -----------------------------------------------------------

def migrate_yaml(store: CodexStore, codex_dir: Path) -> dict:
    """Load modules.yaml, commands.yaml, profiles.yaml into the store."""
    counts = {"modules": 0, "commands": 0, "profiles": 0}

    for yaml_file in sorted(codex_dir.glob("**/*.yaml")):
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        for m in data.get("modules", []):
            store.upsert_module(m)
            counts["modules"] += 1

        for c in data.get("commands", []):
            store.upsert_command(c)
            counts["commands"] += 1

        for p in data.get("profiles", []):
            store.upsert_profile(p)
            counts["profiles"] += 1

    return counts


# -- Notion CSV migration -----------------------------------------------------

_MODULE_MAP = {
    "Modul A: Allgemeine Befehle": "A",
    "Modul B: Programmierung": "B",
    "Modul C: Visualisierung": "C",
    "Modul D: KI-Steuerung": "D",
    "Modul E: Datenanalyse & ML": "E",
    "Modul F: Dokumentation": "F",
    "Modul G: Testing & QA": "G",
    "Modul H: Database & Data Modeling": "H",
    "Modul I: Security & Compliance": "I",
    "Modul J: DevOps & Deployment": "J",
    "Modul K: Frontend & UI": "K",
    "Modul L: Data Pipelines & ETL": "L",
    "Modul M: MCP Integration": "M",
    "Beispiele & Tests": "",
}

_TYPE_MAP = {
    "Dokumentation": "documentation",
    "Beispiel": "example",
    "Test": "test",
    "Referenz": "reference",
}


def migrate_csv(store: CodexStore, csv_path: Path) -> int:
    """Import the Notion CSV export into the catalog table."""
    count = 0
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tags_raw = row.get("Tags", "")
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

            module_raw = row.get("Modul", "")
            module_ref = _MODULE_MAP.get(module_raw, "")

            entry_type = _TYPE_MAP.get(row.get("Typ", ""), "documentation")

            store.add_catalog_entry({
                "title": row.get("Titel", ""),
                "description": row.get("Beschreibung", ""),
                "module_ref": module_ref,
                "tags": tags,
                "entry_type": entry_type,
            })
            count += 1
    return count


# -- CLI -----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Migrate Notion/YAML data to SQLite CodexStore")
    parser.add_argument("--codex-dir", default="codex", help="Codex YAML directory")
    parser.add_argument("--csv", default="data/CompText-Codex.csv", help="Notion CSV export")
    parser.add_argument("--db", default=None, help="Target SQLite database path")
    args = parser.parse_args()

    codex_dir = Path(args.codex_dir)
    csv_path = Path(args.csv)

    store = CodexStore(db_path=args.db)

    print("=== CompText Codex: Notion -> SQLite Migration ===\n")

    # YAML
    if codex_dir.exists():
        print(f"Migrating YAML from {codex_dir} ...")
        yaml_counts = migrate_yaml(store, codex_dir)
        print(f"  Modules:  {yaml_counts['modules']}")
        print(f"  Commands: {yaml_counts['commands']}")
        print(f"  Profiles: {yaml_counts['profiles']}")
    else:
        print(f"  [skip] YAML directory not found: {codex_dir}")

    # CSV
    if csv_path.exists():
        print(f"\nMigrating Notion CSV from {csv_path} ...")
        catalog_count = migrate_csv(store, csv_path)
        print(f"  Catalog entries: {catalog_count}")
    else:
        print(f"\n  [skip] CSV not found: {csv_path}")

    # Also seed commands from the decorator registry
    print("\nSeeding commands from module registry ...")
    from comptext_codex.registry import ensure_modules_loaded, registry
    ensure_modules_loaded()
    for meta in registry.all_module_meta():
        store.upsert_module(meta.to_dict())
    for cmd_meta in registry.all_command_meta():
        store.upsert_command(cmd_meta.to_dict())
    print(f"  Registry modules:  {len(registry.list_module_codes())}")
    print(f"  Registry commands: {len(registry.all_command_meta())}")

    # Summary
    stats = store.stats()
    print(f"\n=== Migration complete ===")
    print(f"  Database: {store._db_path}")
    print(f"  Modules:  {stats['modules']}")
    print(f"  Commands: {stats['commands']}")
    print(f"  Profiles: {stats['profiles']}")
    print(f"  Catalog:  {stats['catalog']}")

    store.close()


if __name__ == "__main__":
    main()
