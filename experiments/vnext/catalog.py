"""CompText Codex vNext: immutable, provenance-preserving catalog generator.

Git-friendly JSON is the reviewed source artifact; SQLite is later a derived
search index, NEVER an executable authority. Historic DB and YAML are read-only.
All import records are unreviewed or quarantined: there is NO automatic approval.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path
from urllib.parse import quote

import yaml

SCHEMA = "comptext.codex.catalog.v1"
SOURCE_COMMIT = "aa59150"
MAX_DB_BYTES = 32 * 1024 * 1024
MAX_YAML_FILES = 4000
MAX_FILE_BYTES = 65536
MAX_OUTPUT_BYTES = 8 * 1024 * 1024


class CatalogError(ValueError):
    """Invalid, incomplete or ambiguous catalog import."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _key(module: str, command: str) -> str:
    cleaned = command.strip().casefold()
    if cleaned.startswith("cmd:"):
        cleaned = cleaned[4:]
    if cleaned.startswith("@"):
        cleaned = cleaned[1:]
    return f"{module}:{cleaned}"


def _json_list(value: str, *, label: str) -> list:
    try:
        obj = json.loads(value)
    except (TypeError, ValueError) as error:
        raise CatalogError(f"invalid {label} list") from error
    if type(obj) is not list or len(obj) > 256 or any(
        type(item) is not str or len(item) > 16384 for item in obj
    ):
        raise CatalogError(f"invalid {label} list")
    return obj


def _load_db(path: Path) -> tuple[list[dict], dict, str]:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_DB_BYTES:
        raise CatalogError("invalid or missing legacy database")
    db_hash = _sha(path.read_bytes())
    uri = "file:" + quote(str(path.resolve()), safe="/") + "?mode=ro&immutable=1"
    try:
        with sqlite3.connect(uri, uri=True, timeout=3) as conn:
            # Actually execute the full small-source integrity check.
            if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise CatalogError("legacy SQLite integrity failure")
            names = {row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
            if not {"commands", "modules", "profiles", "catalog"}.issubset(names):
                raise CatalogError("missing historical database tables")
            rows = conn.execute(
                "SELECT id,module,command,syntax,description,examples,aliases,"
                "token_cost_hint,mcp_exposed FROM commands ORDER BY id"
            ).fetchall()
            counts = {
                "legacy_modules": conn.execute("SELECT COUNT(*) FROM modules").fetchone()[0],
                "legacy_profiles": conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0],
                "legacy_archive_entries": conn.execute("SELECT COUNT(*) FROM catalog").fetchone()[0],
            }
    except (sqlite3.Error, OSError) as error:
        raise CatalogError("failed to read historical database") from error

    records = []
    ids = set()
    for id_, module, command, syntax, description, examples, aliases, token_hint, exposed in rows:
        if type(id_) is not int or id_ in ids or type(module) is not str or not re.fullmatch(
            r"[A-Z]", module
        ) or type(command) is not str or not command.strip() or len(command) > 128:
            raise CatalogError("invalid legacy command identity")
        if any(type(x) is not str for x in (syntax, description)):
            raise CatalogError("invalid legacy description")
        ids.add(id_)
        records.append({
            "legacy_id": id_,
            "module": module,
            "command": command,
            "semantic_key": _key(module, command),
            "syntax": syntax,
            "description": description,
            "examples": _json_list(examples, label="examples"),
            "aliases": _json_list(aliases, label="aliases"),
            "token_cost_hint": int(token_hint),
            "legacy_mcp_exposed": bool(exposed),
        })
    return records, counts, db_hash


def _load_yaml(root: Path) -> tuple[list[dict], str]:
    folder = root / "commands"
    if not folder.is_dir() or folder.is_symlink():
        # Support a folder that directly contains the individual files too.
        folder = root
    if not folder.is_dir() or folder.is_symlink():
        raise CatalogError("missing command YAML directory")
    files = sorted(folder.glob("*.yaml"), key=lambda p: p.name)
    if len(files) > MAX_YAML_FILES:
        raise CatalogError("excessive YAML files")
    parsed = []
    fingerprints = []
    for file in files:
        if file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_FILE_BYTES:
            raise CatalogError("unsafe command YAML file")
        raw = file.read_bytes()
        fingerprints.append({"file":file.name,"sha256":_sha(raw)})
        try:
            data = yaml.safe_load(raw)
        except (yaml.YAMLError, UnicodeError) as error:
            raise CatalogError("invalid command YAML") from error
        if not isinstance(data, dict) or "name" not in data:
            # E.g. basic.yaml is a historical aggregate, not one command file.
            continue
        m = data.get("module_id")
        command = data.get("name")
        if type(m) is not str or not re.fullmatch(r"module:[A-Z]", m) or (
            type(command) is not str or not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", command)
        ):
            raise CatalogError("invalid YAML identity")
        key = _key(m[-1], command)
        parsed.append({
            "semantic_key": key,
            "source_file":file.name,
            "source_sha256":_sha(raw),
            "metadata": data,
        })
    return parsed, _sha(_canonical(fingerprints))


def build_catalog(db_path: str | Path, yaml_root: str | Path) -> dict:
    """Read-only import. Semantic collisions and incomplete specs are quarantined."""
    db_path, yaml_root = Path(db_path), Path(yaml_root)
    legacy, old_counts, legacy_hash = _load_db(db_path)
    yaml_rows, yaml_tree_hash = _load_yaml(yaml_root)
    buckets = collections.defaultdict(list)
    for row in legacy:
        buckets[row["semantic_key"]].append(row)
    yaml_buckets = collections.defaultdict(list)
    for row in yaml_rows:
        yaml_buckets[row["semantic_key"]].append(row)
    collisions = {key for key, entries in buckets.items() if len(entries) > 1}
    yaml_collisions = {key for key, entries in yaml_buckets.items() if len(entries) > 1}
    commands = []
    matched = set()
    for item in legacy:
        key = item["semantic_key"]
        matched_sources = yaml_buckets.get(key, [])
        if matched_sources:
            matched.add(key)
        issues = []
        if key in collisions:
            issues.append("semantic_key_collision")
        if key in yaml_collisions:
            issues.append("yaml_key_collision")
        if any(y["metadata"].get("syntax") != item["syntax"] for y in matched_sources):
            issues.append("syntax_disagreement")
        if not item["syntax"].strip():
            issues.append("missing_syntax")
        if not item["description"].strip():
            issues.append("missing_description")
        if "auto-extracted" in item["description"].casefold():
            issues.append("auto_generated_placeholder")
        quality = "quarantined" if issues else "unreviewed"
        commands.append({
            **item,
            "yaml_provenance": [
                {"file":y["source_file"],"sha256":y["source_sha256"],
                 "metadata":y["metadata"]} for y in matched_sources
            ],
            "quality":quality,
            "issues":issues,
            "runtime_execute_allowed":False,
            "approved_for_mcp_execution":False,
        })
    stats = {
        **old_counts,
        "legacy_rows":len(legacy),
        "legacy_unique_keys":len(buckets),
        "yaml_entries":len(yaml_rows),
        "yaml_matches":len(matched),
        "yaml_orphans":sum(len(v) for k,v in yaml_buckets.items() if k not in buckets),
        "yaml_key_collisions":len(yaml_collisions),
        "key_collision_count":len(collisions),
        "quarantined_rows":sum(x["quality"]=="quarantined" for x in commands),
        "unreviewed_rows":sum(x["quality"]=="unreviewed" for x in commands),
        "auto_authorized_commands":0,
        "notion_api_calls":0,
    }
    core = {
        "schema":SCHEMA,
        "source":{
            "legacy_git_commit":SOURCE_COMMIT,
            "legacy_sha256":legacy_hash,
            "yaml_tree_sha256":yaml_tree_hash,
            "authority":"historical-import-only",
            "current_notion_api_dependency":False,
        },
        "stats":stats,
        "commands":commands,
    }
    result = {**core,"sha256":_sha(_canonical(core))}
    verify_catalog(result)
    return result


def verify_catalog(snapshot: dict) -> bool:
    if type(snapshot) is not dict or set(snapshot) != {
        "schema","source","stats","commands","sha256"
    } or snapshot.get("schema") != SCHEMA:
        raise CatalogError("invalid catalog schema")
    source = snapshot["source"]
    if type(source) is not dict or (
        any(type(source.get(field)) is not str or not re.fullmatch(
            r"[a-f0-9]{64}",source[field]
        ) for field in ("legacy_sha256","yaml_tree_sha256"))
    ):
        raise CatalogError("invalid provenance digest")
    cmds = snapshot["commands"]
    stats = snapshot["stats"]
    if type(cmds) is not list or type(stats) is not dict or (
        stats.get("legacy_rows") != len(cmds) or
        stats.get("auto_authorized_commands") != 0 or
        any(type(x) is not dict or x.get("runtime_execute_allowed") is not False or
            x.get("approved_for_mcp_execution") is not False or
            x.get("quality") not in ("unreviewed","quarantined") for x in cmds)
    ):
        raise CatalogError("catalog validation gate failed")
    if type(snapshot["sha256"]) is not str or snapshot["sha256"] != _sha(_canonical({
        key:snapshot[key] for key in ("schema","source","stats","commands")
    })):
        raise CatalogError("catalog integrity digest mismatch")
    return True


def save_catalog(snapshot: dict, dest: str | Path) -> str:
    verify_catalog(snapshot)
    dest = Path(dest)
    content = _canonical(snapshot) + b"\n"
    if len(content)>MAX_OUTPUT_BYTES:
        raise CatalogError("oversized catalog")
    if dest.exists():
        if dest.read_bytes() == content:
            return "unchanged"
        raise CatalogError("different snapshot exists: refusing overwrite")
    dest.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(dest,os.O_CREAT | os.O_EXCL | os.O_WRONLY,0o600)
    with os.fdopen(fd,"wb") as writer:
        writer.write(content)
        writer.flush()
        os.fsync(writer.fileno())
    return "created"


def load_catalog(path: str | Path) -> dict:
    p=Path(path)
    if not p.is_file() or p.stat().st_size > MAX_OUTPUT_BYTES:
        raise CatalogError("catalog file absent or too large")
    try:
        result=json.loads(p.read_text(encoding="utf8"))
    except (ValueError, UnicodeError) as error:
        raise CatalogError("invalid catalog file") from error
    verify_catalog(result)
    return result


def command_lookup(snapshot: dict, module: str, command: str) -> dict | None:
    verify_catalog(snapshot)
    if type(module) is not str or type(command) is not str:
        return None
    key = _key(module.upper(), command)
    matches=[row for row in snapshot["commands"] if (
        row["semantic_key"] == key and row["quality"] == "unreviewed"
    )]
    return matches[0] if len(matches)==1 else None
