#!/usr/bin/env python3
"""Import YAML command files into SQLite database.

This script reads individual YAML command files from codex/commands/
and imports them into the SQLite database using CodexStore.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import yaml
from comptext_codex.store import CodexStore


def parse_module_id(module_id: str) -> str:
    """Convert module_id like 'module:A' to just 'A'."""
    if module_id.startswith("module:"):
        return module_id[7:]
    return module_id


def import_yaml_commands(commands_dir: Path, store: CodexStore) -> dict:
    """Import all YAML files from commands directory into the store.

    Returns dict with counts of imported and skipped commands.
    """
    stats = {"imported": 0, "skipped": 0, "errors": []}

    yaml_files = list(commands_dir.glob("*.yaml"))
    print(f"Found {len(yaml_files)} YAML files to import")

    for yaml_file in sorted(yaml_files):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                stats["skipped"] += 1
                continue

            # Extract module code from module_id
            module_id = data.get("module_id", "module:A")
            module_code = parse_module_id(module_id)

            # Prepare command dict for store
            cmd = {
                "module": module_code,
                "command": data.get("name", yaml_file.stem),
                "syntax": data.get("syntax", ""),
                "description": data.get("description", ""),
                "examples": data.get("examples", []),
                "aliases": data.get("aliases", []),
                "token_cost_hint": data.get("token_cost_hint", 1),
                "mcp_exposed": data.get("mcp_exposed", True),
            }

            # Clean up examples (remove malformed ones)
            if isinstance(cmd["examples"], list):
                cmd["examples"] = [
                    ex for ex in cmd["examples"]
                    if isinstance(ex, str) and ex.strip()
                ]

            store.upsert_command(cmd)
            stats["imported"] += 1

        except Exception as e:
            stats["errors"].append(f"{yaml_file.name}: {e}")
            stats["skipped"] += 1

    return stats


def main():
    """Main entry point."""
    # Paths
    repo_root = Path(__file__).parent.parent
    commands_dir = repo_root / "codex" / "commands"
    db_path = repo_root / "codex.db"

    if not commands_dir.exists():
        print(f"Error: Commands directory not found: {commands_dir}")
        sys.exit(1)

    print(f"Importing commands from: {commands_dir}")
    print(f"Database: {db_path}")
    print("-" * 50)

    # Initialize store
    store = CodexStore(str(db_path))

    # Check existing stats
    existing = store.stats()
    print(f"Existing data: {existing}")

    # Import commands
    result = import_yaml_commands(commands_dir, store)

    print("-" * 50)
    print(f"Imported: {result['imported']} commands")
    print(f"Skipped: {result['skipped']} files")

    if result["errors"]:
        print(f"\nErrors ({len(result['errors'])}):")
        for err in result["errors"][:10]:
            print(f"  - {err}")
        if len(result["errors"]) > 10:
            print(f"  ... and {len(result['errors']) - 10} more")

    # Final stats
    final = store.stats()
    print(f"\nFinal data: {final}")

    store.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
